import copy,io,json,os,sys,tempfile,unittest
from contextlib import redirect_stdout
from datetime import datetime,timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch
from final.api_503_recovery import RecoveryGeminiGenerator,verify_previous,check_live_budget,register_recovery
from final.gemini_judge_client import GeminiRESTGenerator,ApiFailure,MODEL
from final.prepare_eval_final import canonical_hash

ROOT=Path(__file__).resolve().parents[2]
def config():return json.loads((ROOT/'final/gemini_calibration_config.json').read_text(encoding='utf-8'))


def make_budget(folder,previous):
    path=Path(folder);path.mkdir(exist_ok=True)
    (path/'api_budget_ledger.json').write_text(json.dumps(previous['budget_snapshot']),encoding='utf-8')
    (path/'gemini_calibration_candidate_1.started.json').write_text(json.dumps({'config_sha256':canonical_hash(config())}),encoding='utf-8')


class RecoveryTransport:
    def __init__(self,previous,error=None):self.previous=previous;self.error=error;self.calls=[]
    def __call__(self,method,path,body):
        self.calls.append((method,path,body))
        if method=='GET':return copy.deepcopy(self.previous['metadata']['model_preflight'])
        if path.endswith(':countTokens'):return {'totalTokens':1000}
        if self.error:raise self.error
        return {'candidates':[{'content':{'parts':[{'text':'{"puntaje":2,"razon":"Synthetic test only"}'}]},'finishReason':'STOP'}],
            'modelVersion':MODEL,'usageMetadata':{'promptTokenCount':1000,'totalTokenCount':1200}}


class ApiRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.previous=verify_previous(ROOT)

    def generator(self,temp,transport):
        return RecoveryGeminiGenerator('FAKE',config(),Path(temp)/'api_budget_ledger.json',Path(temp)/'calls.jsonl',
            previous=self.previous,confirmed_free_project=True,transport=transport,
            now_utc=datetime(2026,11,18,tzinfo=timezone.utc),sleeper=lambda s:None,clock=lambda:0)

    def test_original_has_no_verdict_to_select(self):
        self.assertEqual(self.previous['metadata']['generation_http_calls'],1)
        self.assertIsNone(self.previous['metadata']['actual_model_version'])
        self.assertEqual(self.previous['metadata']['last_api_error']['http_status'],503)

    def test_missing_drive_accounting_is_not_reconstructed(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ApiFailure):self.generator(temp,RecoveryTransport(self.previous))
            self.assertFalse((Path(temp)/'api_budget_ledger.json').exists())

    def test_lowered_reservation_or_altered_marker_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            make_budget(temp,self.previous)
            path=Path(temp)/'api_budget_ledger.json';data=json.loads(path.read_text())
            next(iter(data['requests'].values()))['charged_or_reserved_usd']='0'
            path.write_text(json.dumps(data))
            with self.assertRaises(ApiFailure):check_live_budget(temp,config(),self.previous)
            make_budget(temp,self.previous)
            (Path(temp)/'gemini_calibration_candidate_1.started.json').write_text('{}')
            with self.assertRaises(ApiFailure):check_live_budget(temp,config(),self.previous)

    def test_new_marker_does_not_replace_original(self):
        with tempfile.TemporaryDirectory() as temp:
            make_budget(temp,self.previous)
            original=Path(temp)/'gemini_calibration_candidate_1.started.json';before=original.read_bytes()
            register_recovery(temp,config(),self.previous)
            self.assertEqual(original.read_bytes(),before)
            with self.assertRaises(FileExistsError):register_recovery(temp,config(),self.previous)

    def test_budget_sub_limit_includes_original_reservation(self):
        with tempfile.TemporaryDirectory() as temp:
            make_budget(temp,self.previous);client=self.generator(temp,RecoveryTransport(self.previous,error=ApiFailure('api_http_error',503)))
            self.assertEqual(client.stage_start,Decimal(0))
            client.preflight()
            with self.assertRaises(ApiFailure):client.generate('same system','same question')
            self.assertEqual(client.ledger.used_or_reserved(),Decimal('0.6144'))
            self.assertEqual(client.generation_calls,1)
            original_id=next(iter(self.previous['budget_snapshot']['requests']))
            data=json.loads(client.ledger.path.read_text())
            self.assertEqual(data['requests'][original_id],self.previous['budget_snapshot']['requests'][original_id])

    def test_prompt_request_body_identical_to_original_client(self):
        with tempfile.TemporaryDirectory() as temp:
            make_budget(temp,self.previous);client=self.generator(temp,RecoveryTransport(self.previous))
            old=GeminiRESTGenerator('FAKE',config(),Path(temp)/'other_ledger.json',Path(temp)/'other_calls.jsonl',
                confirmed_free_project=True,now_utc=datetime(2026,11,18,tzinfo=timezone.utc))
            self.assertEqual(client.request_body('system','question'),old.request_body('system','question'))

    def test_catalog_change_stops_before_generation(self):
        with tempfile.TemporaryDirectory() as temp:
            make_budget(temp,self.previous);different=copy.deepcopy(self.previous)
            different['metadata']['model_preflight']['version']='different'
            client=self.generator(temp,RecoveryTransport(different))
            with self.assertRaises(ApiFailure):client.preflight()
            self.assertEqual(client.generation_calls,0)

    def test_tampered_archive_rejected_before_inference(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)/'final/evidence/api_07';folder.mkdir(parents=True)
            (folder/'original_results.zip').write_bytes(b'not original')
            with self.assertRaises(ValueError):verify_previous(temp)

    def test_runner_stops_after_one_new_503(self):
        from final import run_gemini_503_recovery as runner
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);budget=folder/'budget';make_budget(budget,self.previous)
            transport=RecoveryTransport(self.previous,error=ApiFailure('api_http_error',503))
            def factory(key,cfg,ledger,audit,**kwargs):
                return RecoveryGeminiGenerator(key,cfg,ledger,audit,**kwargs,transport=transport,
                    now_utc=datetime(2026,11,18,tzinfo=timezone.utc),sleeper=lambda s:None,clock=lambda:0)
            argv=['recovery','--output',str(folder/'results'),'--budget-dir',str(budget),'--confirm-free-project']
            env=dict(os.environ);env.pop('WANDB_API_KEY',None);env['GEMINI_API_KEY']='FAKE'
            with patch.object(sys,'argv',argv),patch.dict(os.environ,env,clear=True),patch.object(runner,'GeminiRESTGenerator',factory),redirect_stdout(io.StringIO()):
                runner.main()
            meta=json.loads((folder/'results/metadata.json').read_text(encoding='utf-8'))
            self.assertEqual(meta['status'],'stopped_api_or_format_failure')
            self.assertEqual(meta['generation_http_calls'],1)
            self.assertEqual(meta['last_api_error']['http_status'],503)
            self.assertEqual(meta['estimated_or_reserved_total_usd'],'0.6144')
            self.assertEqual(len([c for c in transport.calls if c[1].endswith(':generateContent')]),1)


if __name__=='__main__':unittest.main()
