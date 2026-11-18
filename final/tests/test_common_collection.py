import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from final.run_common_collection import collect,CudaMeter
from final.collection_profiles import PathSystem,PROFILES,SETTINGS,build_profile
from final.common_harness import load_common,evaluate
from final.confirmation_final import cases,RULES
from final.prepare_eval_final import canonical_hash
from final.judge_final import rubric_fingerprint

ROOT=Path(__file__).resolve().parents[2]


class Meter:
    def start(self):pass
    def finish(self):return {'wall_seconds':1.0,'peak_cuda_allocated_bytes':123,'peak_cuda_reserved_bytes':456}


class System:
    def __init__(self,error=False):self.calls=[];self.error=error
    def predict(self,question,image=None):
        self.calls.append((question,image))
        if self.error:raise ValueError('PRIVATE_EXCEPTION_CONTENT')
        return {'output':{'respuesta':'Dato','explicacion':'Motivo','citas':[],'abstencion':True},
                'contexts':[],'tool_trace':[],'expected':'NEVER_KEEP','judge_score':5}


class CollectionTests(unittest.TestCase):
    def test_review_preserves_original_pending_and_separate_closure(self):
        pack=ROOT/'final/eval/confirmation_v1'
        approval=json.loads((pack/'human_approval.json').read_text(encoding='utf-8'))
        original=(ROOT/'final/evidence/confirmation_review_01/original_review.md').read_bytes()
        self.assertEqual(hashlib.sha256(original).hexdigest(),approval['original_review_sha256'])
        self.assertIn('confirm_empty_bad: PENDIENTE',original.decode('utf-8'))
        self.assertEqual(len(approval['original_approved_ids']),11)
        self.assertEqual(set(approval['approved_ids']),{c['id'] for c in cases()})
        self.assertEqual(approval['anchors_canonical_sha256'],canonical_hash(cases()))
        self.assertEqual(approval['rules_canonical_sha256'],canonical_hash(RULES))
        self.assertEqual(approval['rubric_sha256'],rubric_fingerprint())
        self.assertFalse(approval['model_inference_performed']);self.assertFalse(approval['judge_validated_for_final'])

    def test_all_22_inputs_no_gold_and_null_quality(self):
        inputs,refs,_=load_common();original=copy.deepcopy(inputs);system=System()
        with tempfile.TemporaryDirectory() as temp:
            rows=collect(inputs,system,Meter(),temp)
            self.assertEqual(len(rows),22);self.assertEqual(inputs,original)
            self.assertTrue(all(set(row['record']).isdisjoint({'expected','judge_score'}) for row in rows))
            self.assertTrue(all(set(args)=={'question','image'} for args in [{'question':q,'image':im} for q,im in system.calls]))
            details,summary=evaluate(rows,refs)
            self.assertIsNone(summary['domain_compliance_rate']);self.assertEqual(summary['judge_valid_count'],0)
            self.assertFalse(summary['quality_accepted']);self.assertTrue(all(d['domain_pass'] is None for d in details))
            self.assertEqual(len((Path(temp)/'predictions.jsonl').read_text().splitlines()),22)
            with self.assertRaises(FileExistsError):collect(inputs,system,Meter(),temp)

    def test_case_error_kept_without_private_exception(self):
        inputs,_,_=load_common()
        with tempfile.TemporaryDirectory() as temp:
            rows=collect(inputs[:2],System(error=True),Meter(),temp)
            self.assertEqual(len(rows),2);self.assertTrue(all(r['system_error_type']=='ValueError' for r in rows))
            self.assertNotIn('PRIVATE_EXCEPTION_CONTENT',(Path(temp)/'predictions.jsonl').read_text())

    def test_measurement_failure_is_saved_and_stops(self):
        class Broken(Meter):
            def finish(self):raise RuntimeError('PRIVATE')
        inputs,_,_=load_common()
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(RuntimeError):collect(inputs[:2],System(),Broken(),temp)
            rows=[json.loads(s) for s in (Path(temp)/'predictions.jsonl').read_text().splitlines()]
            self.assertEqual(len(rows),1);self.assertIsNone(rows[0]['peak_cuda_allocated_bytes'])
            self.assertEqual(rows[0]['measurement_error_type'],'RuntimeError')

    def test_text_baseline_does_not_read_image_or_transcription(self):
        system=System();wrapped=PathSystem(system,False)
        result=wrapped.predict('Q',image=Path('does-not-exist.png'))
        self.assertEqual(system.calls,[]);self.assertEqual(result['guard'],'unsupported_image')
        self.assertTrue(result['output']['abstencion']);self.assertEqual(result['contexts'],[])
        wrapped.predict('Text');self.assertEqual(len(system.calls),1)

    def test_path_image_is_opened_fresh_and_not_cached(self):
        from PIL import Image
        system=System();wrapped=PathSystem(system,True)
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'one.png';Image.new('RGB',(16,16),'red').save(path)
            wrapped.predict('Q',path);wrapped.predict('Q',path)
        self.assertEqual(len(system.calls),2)
        self.assertEqual(system.calls[0][1].getpixel((0,0)),(255,0,0))
        self.assertIsNot(system.calls[0][1],system.calls[1][1])

    def test_cuda_meter_orders_sync_reset_and_reads_real_counters(self):
        calls=[]
        class Cuda:
            def synchronize(self):calls.append('sync')
            def reset_peak_memory_stats(self):calls.append('reset')
            def max_memory_allocated(self):calls.append('allocated');return 100
            def max_memory_reserved(self):calls.append('reserved');return 200
        class Torch:cuda=Cuda()
        meter=CudaMeter(Torch());meter.start();result=meter.finish()
        self.assertEqual(calls,['sync','reset','sync','allocated','reserved'])
        self.assertEqual(result['peak_cuda_allocated_bytes'],100);self.assertGreater(result['wall_seconds'],0)

    def test_profile_names_and_explicit_non_final_protocol(self):
        self.assertEqual(len(PROFILES),5);self.assertEqual(SETTINGS['max_new_tokens'],512)
        self.assertFalse(SETTINGS['judge_used']);self.assertFalse(SETTINGS['semantic_protocol_frozen'])
        with self.assertRaises(ValueError):build_profile('not-a-profile',[],None,None)

    def test_predeclared_controls_match_references_without_declaring_execution(self):
        _,refs,_=load_common()
        rules=json.loads((ROOT/'final/domain_protocol_v1.json').read_text(encoding='utf-8'))
        self.assertEqual(set(rules['controls']['abstention_ids']),{r['id'] for r in refs if r['expected_abstention']})
        self.assertEqual(rules['controls']['adversarial_ids'],['vis_07_injection'])
        self.assertIn('pending',rules['status'])
        self.assertIn('raw_judge_score_at_least_4_from_validated_judge',rules['domain_pass_requires_all'])

    def test_duplicate_inputs_rejected_before_creating_result_file(self):
        inputs,_,_=load_common()
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):collect([inputs[0],inputs[0]],System(),Meter(),temp)
            self.assertFalse((Path(temp)/'predictions.jsonl').exists())

    def test_baselines_construct_real_historical_variant_without_retrieval(self):
        from final import generators
        spy=System()
        class Rag:
            def predict(self,question,retrieve=True):spy.calls.append(retrieve);return {'output':None}
        class Generator:
            def __init__(self,*args,**kwargs):self.precision=kwargs['precision']
            def close(self):pass
        class Dense:chunks={}
        with patch.object(generators,'CausalGenerator',Generator),patch('sistemas_m3.construir',return_value={'sin_rag':Rag(),'sistema_final':System()}):
            system,gen,vision=build_profile('qa_no_rag_fp16',[],Dense(),None)
            system.predict('Q');self.assertEqual(spy.calls,[False]);self.assertIsNone(vision)
            self.assertEqual(gen.precision,'fp16')

    def test_visual_pair_changes_only_precision_and_ablation_bypasses_tool_route(self):
        from final import generators,adapters
        from unittest.mock import MagicMock
        loaded=[]
        class Generator:
            def __init__(self,*args,**kwargs):self.kwargs=kwargs;self.last_generation={};loaded.append(self)
            def generate(self,system,user):return json.dumps(System().predict('Q')['output'])
            def close(self):self.closed=True
        class Dense:chunks={}
        class Vision:
            def close(self):pass
        retriever=MagicMock();retriever.search.return_value=[]
        with patch.object(generators,'NativeChatGenerator',Generator),patch.object(adapters,'Vision',Vision),\
                patch('retrieval_advanced.HybridRetriever'),patch('retrieval_advanced.RerankedRetriever'),\
                patch.object(adapters,'CompleteFieldRetriever',return_value=retriever):
            left,_,_=build_profile('integrated_fp16',[],Dense(),None)
            right,_,_=build_profile('integrated_nf4',[],Dense(),None)
            self.assertEqual(loaded[0].kwargs,{'precision':'fp16','max_new_tokens':512})
            self.assertEqual(loaded[1].kwargs,{'precision':'nf4','max_new_tokens':512})
            ablation,_,_=build_profile('integrated_no_tool_fp16',[],Dense(),None)
            with patch.object(adapters.AnswerAdapter,'__call__',side_effect=AssertionError('Router must not be called')):
                result=ablation.system.answer('¿Cuál es la diferencia absoluta entre dos valores?')
            self.assertEqual(result['tool_policy'],'ablation_disabled');self.assertEqual(result['tool_trace'],[])

    def test_failed_visual_load_closes_generator_without_fallback(self):
        from final import generators,adapters
        loaded=[]
        class Generator:
            def __init__(self,*args,**kwargs):self.closed=False;loaded.append(self)
            def close(self):self.closed=True
        with patch.object(generators,'NativeChatGenerator',Generator),patch.object(adapters,'Vision',side_effect=RuntimeError('failure')):
            with self.assertRaises(RuntimeError):build_profile('integrated_nf4',[],None,None)
        self.assertTrue(loaded[0].closed);self.assertEqual(len(loaded),1)


if __name__=='__main__':unittest.main()
