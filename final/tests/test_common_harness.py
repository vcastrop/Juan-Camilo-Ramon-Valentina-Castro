import copy,json,unittest
from final.common_harness import load_common,infer,evaluate,automatic,fact_present,judge_packet


def out(answer='Entidad X',abstention=False):
    return {'respuesta':answer,'explicacion':'Se encuentra en la ficha.','citas':['C::one'],'abstencion':abstention}


def reference(cid='t1'):
    return {'id':cid,'kind':'factual','input_modality':'text','source_ids':['C'],
        'required_facts':['Entidad X'],'expected_abstention':False,'pair_with':None}


def record(answer='Entidad X'):
    return {'question':'¿Qué entidad?','output':out(answer),
        'contexts':[{'chunk_id':'C::one','doc_id':'C','text':'Entidad: Entidad X'}],'tool_trace':[]}


class CommonHarnessTests(unittest.TestCase):
    def test_real_package_hashes_and_images(self):
        inputs,refs,meta=load_common()
        self.assertEqual((len(inputs),len(refs),meta['cases']),(22,22,22))

    def test_only_inputs_cross_system_boundary(self):
        class System:
            def predict(self,question,**kwargs):
                self.args=(question,kwargs);return dict(record(),expected='SECRET')
        system=System();rows=infer([{'id':'t1','question':'Question','image':None,'expected':'SECRET'}],system)
        self.assertEqual(system.args,('Question',{'image':None}))
        self.assertNotIn('expected',rows[0]['record'])

    def test_error_remains_in_denominator(self):
        class System:
            def predict(self,*args,**kwargs):raise RuntimeError('sensitive body')
        rows=infer([{'id':'t1','question':'Question','image':None}],System())
        self.assertEqual(rows[0]['system_error_type'],'RuntimeError')
        self.assertNotIn('sensitive',json.dumps(rows))
        _,summary=evaluate(rows,[reference()])
        self.assertEqual(summary['literal_fact_coverage_mean'],0)
        self.assertIsNone(summary['domain_compliance_rate'])

    def test_number_boundaries_separators_decimals_and_negation(self):
        for text in ['85000 COP','85.000 COP','85,000 COP','85000.']:
            self.assertTrue(fact_present('85000',text),text)
        for text in ['850000 COP','85000.50 COP','-85000 COP','No es 85000 COP']:
            self.assertFalse(fact_present('85000',text),text)
        self.assertFalse(fact_present('mínima cuantía','No es mínima cuantía'))

    def test_explanation_cannot_rescue_wrong_answer_or_abstention(self):
        rec=record('Otra entidad');rec['output']['explicacion']='Entidad X'
        self.assertEqual(automatic(reference(),rec)['literal_fact_coverage'],0)
        rec=record();rec['output']['abstencion']=True
        self.assertEqual(automatic(reference(),rec)['literal_fact_coverage'],0)

    def test_citation_existence_is_not_semantic_entailment(self):
        rec=record();rec['contexts'][0]['text']='No contiene la entidad.'
        result=automatic(reference(),rec)
        self.assertTrue(result['traceability_pass'])
        # Automatic diagnostics deliberately do not claim that citations entail content.
        _,summary=evaluate([{'id':'t1','record':rec}],[reference()])
        self.assertFalse(summary['quality_accepted'])

    def test_missing_prediction_and_duplicate_not_hidden(self):
        details,summary=evaluate([],[reference()])
        self.assertEqual(summary['case_count'],1)
        self.assertEqual(details[0]['system_error_type'],'MissingPrediction')
        item={'id':'t1','record':record()}
        with self.assertRaises(ValueError):evaluate([item,item],[reference()])

    def test_judge_never_gets_reference_fields_and_raw_score_not_adjusted(self):
        class Judge:
            def evaluate(self,rec):
                self.rec=rec
                return {'score':5,'reason':'Experimental'}
        judge=Judge();ref=dict(reference(),expected='GOLD',criterion='SECRET')
        details,summary=evaluate([{'id':'t1','record':record('Incorrecta')}],[ref],judge)
        self.assertNotIn('GOLD',json.dumps(judge.rec))
        self.assertNotIn('SECRET',json.dumps(judge.rec))
        self.assertEqual(details[0]['judge']['score'],5)
        self.assertEqual(summary['judge_mean_raw_experimental'],5)
        self.assertIsNone(details[0]['domain_pass'])

    def test_tool_trace_is_whitelisted(self):
        rec=record();rec['tool_trace']=[{'expected':'GOLD','tool_result':{'ok':True,'operation':'1-1=0','expected':'GOLD'}}]
        self.assertNotIn('GOLD',json.dumps(judge_packet(rec)))

    def test_invariance_is_not_correctness(self):
        a=reference('a');b=reference('b');b['pair_with']='a'
        rows=[{'id':cid,'record':record('Incorrecta')} for cid in ['a','b']]
        _,summary=evaluate(rows,[a,b])
        self.assertTrue(summary['invariance_pairs'][0]['output_invariant'])
        self.assertFalse(summary['invariance_pairs'][0]['both_automatic_checks_pass'])

    def test_invalid_judge_score_is_unknown_not_fabricated(self):
        class Judge:
            def evaluate(self,rec):return {'score':True}
        details,summary=evaluate([{'id':'t1','record':record()}],[reference()],Judge())
        self.assertIsNone(details[0]['judge'])
        self.assertIsNone(summary['judge_mean_raw_experimental'])

    def test_image_path_escape_does_not_call_system(self):
        class System:
            def predict(self,*args,**kwargs):raise AssertionError('Must not be called')
        rows=infer([{'id':'t1','question':'Q','image':'../outside.png','image_sha256':'x'}],System())
        self.assertEqual(rows[0]['system_error_type'],'ValueError')

    def test_malformed_contexts_fail_traceability_without_crashing(self):
        for bad in [None,'not a list',[{'chunk_id':'C::one'}],[record()['contexts'][0]]*2]:
            rec=record();rec['contexts']=bad
            self.assertFalse(automatic(reference(),rec)['traceability_pass'])

    def test_missing_rows_keep_reference_order(self):
        details,_=evaluate([],[reference('z'),reference('a')])
        self.assertEqual([d['id'] for d in details],['z','a'])


if __name__=='__main__':unittest.main()
