import copy,hashlib,json,tempfile,unittest
from datetime import datetime,timezone
from decimal import Decimal
from pathlib import Path
from final.hydrogen_resume import (verify_checkpoint,register_resume,ResumableHydrogenGenerator,
    safe_error_details,POLICY)
from final.gemini_judge_client import ApiFailure
from final.prepare_eval_final import canonical_hash
from final.tests.test_hydrogen_judge import config,budget,Transport

ROOT=Path(__file__).resolve().parents[2]


class ResumeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.checkpoint=verify_checkpoint(ROOT)

    def setup_drive(self,temp):
        budget(temp,self.checkpoint['base_drive'])
        (Path(temp)/'hydrogen_calibration_candidate_1.started.json').write_text(
            json.dumps({'config_sha256':canonical_hash(config())}),encoding='utf-8')

    def client(self,temp,errors=(),score=2):
        transport=Transport(score=score);pending=list(errors)
        def send(method,path,body):
            if method=='GET':return copy.deepcopy(self.checkpoint['metadata']['model_preflight'])
            if path.endswith(':generateContent') and pending:
                error=pending.pop(0)
                if error:raise error
            return transport(method,path,body)
        waits=[]
        client=ResumableHydrogenGenerator('FAKE',config(),Path(temp)/'api_budget_ledger.json',Path(temp)/'calls.jsonl',
            checkpoint=self.checkpoint,confirmed_free_project=True,transport=send,
            now_utc=datetime(2026,11,18,tzinfo=timezone.utc),clock=lambda:0,
            sleeper=waits.append,jitter=lambda:0)
        client.preflight()
        return client,waits

    def test_checkpoint_keeps_only_valid_note_and_request_payload(self):
        saved=self.checkpoint['saved_rows']
        self.assertEqual(len(saved),1);self.assertEqual(saved[0]['id'],'attribution_bad')
        self.assertEqual(saved[0]['judgement']['score'],2)
        from final.calibration_final import cases
        from final.judge_final import FinalJudge
        from final.reasoning_calibration import request_seed
        from m3.judge import evidence_payload
        record=next(c['record'] for c in cases() if c['id']=='attribution_good')
        with tempfile.TemporaryDirectory() as temp:
            self.setup_drive(temp);client,_=self.client(temp)
            client.set_request_seed(request_seed('attribution_good',42))
            judge=FinalJudge(client)
            body=client.request_body(judge.system,json.dumps(evidence_payload(record),ensure_ascii=False))
            digest=hashlib.sha256(json.dumps(body,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
            self.assertEqual(digest,'9f5a82938ae3efda77aea6c6c53045266802da363892446302056361b37ac1b5')

    def test_marker_preserves_prior_accounting_and_blocks_repeat(self):
        with tempfile.TemporaryDirectory() as temp:
            self.setup_drive(temp);before={p.name:p.read_bytes() for p in Path(temp).iterdir()}
            register_resume(temp,config(),self.checkpoint)
            with self.assertRaises(FileExistsError):register_resume(temp,config(),self.checkpoint)
            for name,data in before.items():self.assertEqual((Path(temp)/name).read_bytes(),data)

    def test_missing_marker_or_changed_ledger_blocks(self):
        with tempfile.TemporaryDirectory() as temp:
            self.setup_drive(temp)
            (Path(temp)/'hydrogen_calibration_candidate_1.started.json').unlink()
            with self.assertRaises(ApiFailure):register_resume(temp,config(),self.checkpoint)
            ledger=Path(temp)/'api_budget_ledger.json';ledger.write_text('{}')
            with self.assertRaises(ApiFailure):self.client(temp)

    def test_503_then_success_keeps_old_reservation(self):
        with tempfile.TemporaryDirectory() as temp:
            self.setup_drive(temp);client,waits=self.client(temp,[ApiFailure('api_http_error',503)])
            self.assertEqual(json.loads(client.generate('s','u'))['puntaje'],2)
            self.assertEqual(client.generation_calls,2);self.assertEqual(client.retry_count,1)
            self.assertIn(30,waits);self.assertIsNone(client.last_error)
            self.assertEqual(client.ledger.used_or_reserved(),Decimal('1.8652725'))
            data=json.loads(client.ledger.path.read_text())
            for key,value in self.checkpoint['budget_snapshot']['requests'].items():
                self.assertEqual(data['requests'][key],value)

    def test_two_global_retries_not_per_case(self):
        with tempfile.TemporaryDirectory() as temp:
            self.setup_drive(temp)
            client,waits=self.client(temp,[ApiFailure('api_http_error',503),None,ApiFailure('api_http_error',503),ApiFailure('api_http_error',503)])
            client.generate('s','u')
            with self.assertRaises(ApiFailure):client.generate('s','u2')
            self.assertEqual(client.retry_count,2);self.assertEqual(client.generation_calls,4)
            self.assertIn(30,waits);self.assertIn(60,waits)

    def test_three_503_stop_with_all_reservations_retained(self):
        with tempfile.TemporaryDirectory() as temp:
            self.setup_drive(temp);client,_=self.client(temp,[ApiFailure('api_http_error',503)]*3)
            with self.assertRaises(ApiFailure):client.generate('s','u')
            self.assertEqual(client.generation_calls,3)
            self.assertEqual(client.ledger.used_or_reserved(),Decimal('3.0850725'))
            with self.assertRaises(ApiFailure) as error:client.generate('s','u')
            self.assertEqual(error.exception.code,'calibration_estimate_budget_exhausted')
            self.assertEqual(client.generation_calls,3)
            self.assertEqual(json.loads(client.ledger.path.read_text())['limit_usd'],'5.00')

    def test_other_failures_never_retried(self):
        for status in [400,401,403,404,429,None]:
            with self.subTest(status=status),tempfile.TemporaryDirectory() as temp:
                self.setup_drive(temp);client,_=self.client(temp,[ApiFailure('test',status)])
                with self.assertRaises(ApiFailure):client.generate('s','u')
                self.assertEqual(client.retry_count,0);self.assertEqual(client.generation_calls,1)

    def test_wrong_grade_is_returned_unchanged_once(self):
        with tempfile.TemporaryDirectory() as temp:
            self.setup_drive(temp);client,_=self.client(temp,score=4)
            self.assertEqual(json.loads(client.generate('s','u'))['puntaje'],4)
            self.assertEqual(client.generation_calls,1)

    def test_provider_message_is_not_retained(self):
        details=safe_error_details(json.dumps({'error':{'status':'UNAVAILABLE',
            'message':'overloaded FAKE_SECRET question private'}}),{'Retry-After':'31'})
        self.assertEqual(details,{'provider_status':'UNAVAILABLE','provider_message_category':'overload','retry_after_seconds':31})
        self.assertNotIn('FAKE_SECRET',json.dumps(details))
        self.assertEqual(safe_error_details(b'not-json',{}),{})

    def test_runner_stops_safely_and_preserves_checkpoint_end_to_end(self):
        import io,os
        from contextlib import redirect_stdout
        from unittest.mock import patch
        from final import run_hydrogen_continuation as runner
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);drive=folder/'drive';drive.mkdir();self.setup_drive(drive)
            client,_=self.client(drive,[ApiFailure('api_http_error',503)]*3)
            result=folder/'results'
            with patch.object(runner,'GeminiRESTGenerator',return_value=client),patch('sys.argv',[
                    'runner','--output',str(result),'--budget-dir',str(drive),'--confirm-free-project']),\
                    patch.dict(os.environ,{'GEMINI_API_KEY':'FAKE','WANDB_API_KEY':''}),redirect_stdout(io.StringIO()):
                runner.main()
            rows=[json.loads(s) for s in (result/'raw_judgements.jsonl').read_text(encoding='utf-8').splitlines()]
            meta=json.loads((result/'metadata.json').read_text())
            self.assertEqual(rows[0]['judgement'],self.checkpoint['saved_rows'][0]['judgement'])
            self.assertFalse(rows[0]['provenance']['regenerated'])
            self.assertEqual(rows[1]['id'],'attribution_good');self.assertIsNone(rows[1]['judgement']['score'])
            self.assertEqual(meta['judgements_executed'],1);self.assertEqual(meta['reused_valid_judgements'],1)
            self.assertEqual(meta['generation_http_calls'],3);self.assertEqual(meta['technical_503_retries_used'],2)
            self.assertEqual(meta['status'],'stopped_api_or_format_failure')
            self.assertEqual(meta['estimated_or_reserved_total_usd'],'3.0850725')
            self.assertFalse(meta['judge_validated_for_final'])
            self.assertEqual(json.loads((result/'resume_policy.json').read_text()),POLICY)

    def test_catalog_changes_block_continuation(self):
        with tempfile.TemporaryDirectory() as temp:
            self.setup_drive(temp);client,_=self.client(temp)
            client.checkpoint=copy.deepcopy(self.checkpoint)
            client.checkpoint['metadata']['model_preflight']['version']='changed'
            with self.assertRaises(ApiFailure):client.preflight()
            self.assertEqual(client.generation_calls,0)


if __name__=='__main__':unittest.main()
