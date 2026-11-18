import copy,json,tempfile,unittest,os,subprocess,sys
from datetime import datetime,timezone
from decimal import Decimal
from pathlib import Path
from final.gemini_judge_client import GeminiRESTGenerator,ApiFailure,MODEL,public_response,validate_config
from final.run_gemini_calibration import pilot_summary,register_experiment
from final.judge_final import FinalJudge
from final.calibration_final import cases

ROOT=Path(__file__).resolve().parents[2]


def config():return json.loads((ROOT/'final/gemini_calibration_config.json').read_text(encoding='utf-8'))


def reply(text='{"puntaje":2,"razon":"Atribución falsa de campo."}',version=MODEL):
    return {'candidates':[{'content':{'parts':[{'thought':True,'text':'PRIVATE_THOUGHT_NOT_TO_STORE'},
          {'text':text,'thoughtSignature':'PRIVATE_SIGNATURE_NOT_TO_STORE'}]},'finishReason':'STOP'}],
        'modelVersion':version,'usageMetadata':{'totalTokenCount':1200,'promptTokenCount':1000,'thoughtsTokenCount':100,'candidatesTokenCount':100}}


class FakeTransport:
    def __init__(self,responses=None,error=None):self.calls=[];self.responses=iter(responses or [reply()]);self.error=error
    def __call__(self,method,path,body):
        self.calls.append((method,path,body))
        if method=='GET':return {'name':'models/'+MODEL,'version':'001','inputTokenLimit':1048576,'outputTokenLimit':65536,'supportedGenerationMethods':['generateContent','countTokens']}
        if path.endswith(':countTokens'):return {'totalTokens':1000}
        if self.error:raise self.error
        return next(self.responses)


class GeminiJudgeTests(unittest.TestCase):
    def client(self,temp,transport,**kwargs):
        return GeminiRESTGenerator('SECRET_TEST_KEY',config(),Path(temp)/'ledger.json',Path(temp)/'calls.jsonl',
            confirmed_free_project=True,transport=transport,sleeper=lambda seconds:None,clock=lambda:0,
            now_utc=datetime(2026,11,18,tzinfo=timezone.utc),**kwargs)

    def test_no_free_attestation_means_no_network(self):
        fake=FakeTransport()
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ApiFailure):GeminiRESTGenerator('KEY',config(),Path(temp)/'l',Path(temp)/'a',transport=fake)
        self.assertEqual(fake.calls,[])

    def test_strict_model_no_auto_fallback(self):
        cfg=config();cfg['model']='another-model'
        with self.assertRaises(ValueError):validate_config(cfg)

    def test_http_request_body_no_secrets_gold_sampling_or_tools(self):
        with tempfile.TemporaryDirectory() as temp:
            client=self.client(temp,FakeTransport());body=client.request_body('system','user')
            self.assertNotIn('SECRET_TEST_KEY',json.dumps(body))
            self.assertNotIn('tools',body)
            self.assertNotIn('temperature',body['generationConfig'])
            self.assertFalse(body['generationConfig']['thinkingConfig']['includeThoughts'])
            self.assertEqual(body['generationConfig']['candidateCount'],1)

    def test_public_json_only_private_text_and_signatures_not_saved(self):
        with tempfile.TemporaryDirectory() as temp:
            fake=FakeTransport();client=self.client(temp,fake);client.preflight()
            text=client.generate('system','user')
            audit=(Path(temp)/'calls.jsonl').read_text(encoding='utf-8')
            self.assertEqual(json.loads(text)['puntaje'],2)
            self.assertNotIn('PRIVATE_',audit);self.assertNotIn('SECRET_TEST_KEY',audit)
            self.assertEqual(client.ledger.used_or_reserved(),Decimal('0.0045'))
            self.assertEqual(client.generation_calls,1)

    def test_transport_error_keeps_reservation_and_does_not_retry(self):
        with tempfile.TemporaryDirectory() as temp:
            fake=FakeTransport(error=ApiFailure('api_http_error',429));client=self.client(temp,fake);client.preflight()
            with self.assertRaises(ApiFailure):client.generate('s','u')
            self.assertEqual(client.generation_calls,1)
            self.assertEqual(client.ledger.used_or_reserved(),Decimal('0.3072'))

    def test_managed_version_change_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            client=self.client(temp,FakeTransport([reply(version=MODEL+'-001'),reply(version=MODEL+'-002')]))
            client.preflight();client.generate('s','u')
            with self.assertRaises(ApiFailure):client.generate('s','u')

    def test_unexpected_model_does_not_pass_preflight(self):
        with tempfile.TemporaryDirectory() as temp:
            client=self.client(temp,lambda *args:{'name':'models/other'})
            with self.assertRaises(ApiFailure):client.preflight()
            self.assertEqual(client.generation_calls,0)

    def test_truncation_not_scored_or_retried(self):
        response=reply();response['candidates'][0]['finishReason']='MAX_TOKENS'
        with tempfile.TemporaryDirectory() as temp:
            client=self.client(temp,FakeTransport([response]));client.preflight()
            result=FinalJudge(client).evaluate(cases()[0]['record'])
            self.assertIsNone(result['score']);self.assertEqual(client.generation_calls,1)
            self.assertIn('raw_final',(Path(temp)/'calls.jsonl').read_text(encoding='utf-8'))

    def test_false_explanation_score_four_is_kept_and_fails_pilot(self):
        with tempfile.TemporaryDirectory() as temp:
            fake=FakeTransport([reply('{"puntaje":4,"razon":"Incorrecta atribución."}')])
            client=self.client(temp,fake);client.preflight()
            record=next(c['record'] for c in cases() if c['id']=='attribution_bad')
            record=copy.deepcopy(record);record['expected']='NEVER_SEND_GOLD'
            judgement=FinalJudge(client).evaluate(record)
            self.assertEqual(judgement['score'],4)
            self.assertFalse(pilot_summary([{'id':'attribution_bad','judgement':judgement}],['attribution_bad'])['pilot_passed'])
            self.assertNotIn('NEVER_SEND_GOLD',json.dumps(fake.calls))

    def test_pilot_does_not_approve_missing_cases(self):
        result=pilot_summary([{'id':'attribution_bad','judgement':{'score':2}}],config()['pilot_ids'])
        self.assertFalse(result['pilot_passed'])
        self.assertEqual(len(result['unexecuted_ids']),8)

    def test_persistent_marker_prevents_fresh_session_rerun(self):
        with tempfile.TemporaryDirectory() as temp:
            path=register_experiment(temp,config());old=path.read_bytes()
            with self.assertRaises(FileExistsError):register_experiment(temp,config())
            self.assertEqual(path.read_bytes(),old)

    def test_expired_price_requires_review(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ApiFailure):
                GeminiRESTGenerator('KEY',config(),Path(temp)/'l',Path(temp)/'a',confirmed_free_project=True,
                    now_utc=datetime(2027,1,1,tzinfo=timezone.utc))

    def test_runner_without_secret_stops_before_model_or_api(self):
        with tempfile.TemporaryDirectory() as temp:
            env=dict(os.environ);env.pop('GEMINI_API_KEY',None);env.pop('WANDB_API_KEY',None)
            output=Path(temp)/'results'
            proc=subprocess.run([sys.executable,str(ROOT/'final/run_gemini_calibration.py'),
                '--output',str(output),'--budget-dir',str(Path(temp)/'budget'),'--confirm-free-project'],
                cwd=ROOT,env=env,capture_output=True,text=True)
            self.assertEqual(proc.returncode,1)
            meta=json.loads((output/'metadata.json').read_text(encoding='utf-8'))
            self.assertEqual(meta['api_error_code'],'missing_gemini_api_key')
            self.assertEqual(meta['judgements_executed'],0)
            self.assertFalse((output/'api_requests.jsonl').exists())


if __name__=='__main__':unittest.main()
