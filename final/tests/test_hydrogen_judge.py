import copy,json,tempfile,unittest
from datetime import datetime,timezone
from decimal import Decimal
from pathlib import Path
from final.hydrogen_history import verify_history,check_drive,register_hydrogen
from final.gemini_judge_client import ApiFailure
from final.judge_final import FinalJudge
from final.calibration_final import cases
from final.prepare_eval_final import canonical_hash

ROOT=Path(__file__).resolve().parents[2]


def config():return json.loads((ROOT/'final/hydrogen_calibration_config.json').read_text(encoding='utf-8'))


def budget(folder,previous):
    folder=Path(folder)
    (folder/'api_budget_ledger.json').write_text(json.dumps(previous['budget_snapshot']),encoding='utf-8')
    for name in ['gemini_calibration_candidate_1.started.json','gemini_calibration_candidate_1_503_recovery.started.json']:
        (folder/name).write_text(json.dumps({'config_sha256':previous['metadata']['config_canonical_sha256']}),encoding='utf-8')


class Transport:
    def __init__(self,score=2,error=None):self.calls=[];self.score=score;self.error=error
    def __call__(self,method,path,body):
        self.calls.append((method,path,body))
        if method=='GET':return {'name':'models/gemini-4-hydrogen','version':'4.0','inputTokenLimit':1048576,
            'outputTokenLimit':1048576,'supportedGenerationMethods':['generateContent','countTokens']}
        if path.endswith(':countTokens'):return {'totalTokens':1000}
        if self.error:raise self.error
        return {'modelVersion':'gemini-4-hydrogen','usageMetadata':{'promptTokenCount':1000,'totalTokenCount':1200},
            'candidates':[{'finishReason':'STOP','content':{'parts':[{'thought':True,'text':'PRIVATE'},
                {'text':json.dumps({'puntaje':self.score,'razon':'Synthetic unit-test verdict'})}]}}]}


class HydrogenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.previous=verify_history(ROOT)

    def client(self,temp,transport):
        from final.hydrogen_judge_client import HydrogenRESTGenerator
        return HydrogenRESTGenerator('FAKE',config(),Path(temp)/'api_budget_ledger.json',Path(temp)/'calls.jsonl',
            previous=self.previous,confirmed_free_project=True,transport=transport,
            now_utc=datetime(2026,11,18,tzinfo=timezone.utc),clock=lambda:0,sleeper=lambda s:None)

    def test_configuration_and_schema_native_no_unused_sampling(self):
        from final.hydrogen_judge_client import validate_config
        cfg=config();validate_config(cfg)
        cfg['total_authorized_usd']='10.00'
        with self.assertRaises(ValueError):validate_config(cfg)
        with tempfile.TemporaryDirectory() as temp:
            budget(temp,self.previous);client=self.client(temp,Transport());body=client.request_body('system','user')
            self.assertEqual(body['generationConfig']['maxOutputTokens'],65536)
            self.assertNotIn('candidateCount',body['generationConfig'])
            self.assertNotIn('temperature',body['generationConfig'])
            self.assertIn('responseJsonSchema',body['generationConfig'])

    def test_two_prior_reservations_verified_and_missing_drive_blocks(self):
        self.assertEqual(len(self.previous['budget_snapshot']['requests']),2)
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ApiFailure):self.client(temp,Transport())
            self.assertFalse((Path(temp)/'api_budget_ledger.json').exists())

    def test_new_marker_keeps_old_markers_and_blocks_rerun(self):
        with tempfile.TemporaryDirectory() as temp:
            budget(temp,self.previous)
            original={p.name:p.read_bytes() for p in Path(temp).glob('*.started.json')}
            register_hydrogen(temp,config(),self.previous)
            with self.assertRaises(FileExistsError):register_hydrogen(temp,config(),self.previous)
            for name,value in original.items():self.assertEqual((Path(temp)/name).read_bytes(),value)

    def test_current_model_output_limit_can_be_unified_one_million_but_request_is_bounded(self):
        with tempfile.TemporaryDirectory() as temp:
            budget(temp,self.previous);client=self.client(temp,Transport());client.preflight()
            self.assertEqual(client.model_info['outputTokenLimit'],1048576)
            result=client.generate('system','user')
            self.assertEqual(json.loads(result)['puntaje'],2)
            self.assertEqual(client.ledger.used_or_reserved(),Decimal('0.6234'))
            self.assertEqual(client.stage_start,Decimal(0))
            text=(Path(temp)/'calls.jsonl').read_text(encoding='utf-8')
            self.assertNotIn('PRIVATE',text)

    def test_failure_keeps_all_three_reservations_without_retry(self):
        with tempfile.TemporaryDirectory() as temp:
            budget(temp,self.previous);client=self.client(temp,Transport(error=ApiFailure('api_http_error',503)))
            client.preflight()
            with self.assertRaises(ApiFailure):client.generate('s','u')
            self.assertEqual(client.generation_calls,1)
            self.assertEqual(client.ledger.used_or_reserved(),Decimal('1.2288'))

    def test_new_calibration_sub_limit_is_accumulated_not_reset(self):
        with tempfile.TemporaryDirectory() as temp:
            budget(temp,self.previous);client=self.client(temp,Transport());client.preflight();client.ledger.reserve('1')
            with self.assertRaises(ApiFailure):client.generate('s','u')
            self.assertEqual(client.generation_calls,0)

    def test_wrong_score_is_never_corrected_by_api_wrapper(self):
        with tempfile.TemporaryDirectory() as temp:
            budget(temp,self.previous);fake=Transport(score=4);client=self.client(temp,fake);client.preflight()
            record=copy.deepcopy(next(c['record'] for c in cases() if c['id']=='attribution_bad'))
            record['expected']='NEVER_SEND_GOLD'
            result=FinalJudge(client).evaluate(record)
            self.assertEqual(result['score'],4)
            self.assertFalse(result['score_adjusted'])
            self.assertNotIn('NEVER_SEND_GOLD',json.dumps(fake.calls))

    def test_altered_prior_ledger_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            budget(temp,self.previous);path=Path(temp)/'api_budget_ledger.json'
            data=json.loads(path.read_text());data['requests'].clear();path.write_text(json.dumps(data))
            with self.assertRaises(ApiFailure):check_drive(temp,self.previous)

    def test_missing_api_verdict_is_invalid_not_semantic_failure(self):
        from final.run_hydrogen_calibration import pilot_summary
        result=pilot_summary([{'id':'attribution_bad','judgement':{'score':None}}],['attribution_bad'])
        self.assertFalse(result['pilot_passed'])
        self.assertEqual(result['failed_ids'],[])
        self.assertEqual(result['invalid_ids'],['attribution_bad'])
        wrong=pilot_summary([{'id':'attribution_bad','judgement':{'score':4}}],['attribution_bad'])
        self.assertEqual(wrong['failed_ids'],['attribution_bad'])


if __name__=='__main__':unittest.main()
