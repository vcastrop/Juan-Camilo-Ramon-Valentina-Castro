import hashlib,io,json,tempfile,unittest,urllib.error
from datetime import datetime,timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch,MagicMock
from final.hydrogen_recovery11 import verify_checkpoint,register_resume,RecoveryGenerator,POLICY
from final.gemini_judge_client import ApiFailure
from final.tests.test_hydrogen_judge import config,budget,Transport
from final.prepare_eval_final import canonical_hash

ROOT=Path(__file__).resolve().parents[2]


class RecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.checkpoint=verify_checkpoint(ROOT)

    def setup_drive(self,folder):
        budget(folder,self.checkpoint['base_drive'])
        data={'config_sha256':canonical_hash(config()),'checkpoint_sha256':self.checkpoint['archive_sha256']}
        for name in ['hydrogen_calibration_candidate_1.started.json','hydrogen_calibration_resume_1.started.json']:
            (Path(folder)/name).write_text(json.dumps(data),encoding='utf-8')

    def client(self,folder,errors=(),score=2):
        pending=list(errors);fake=Transport(score=score)
        def send(method,path,body):
            if method=='GET':return self.checkpoint['metadata']['model_preflight']
            if path.endswith(':generateContent') and pending:
                error=pending.pop(0)
                if error:raise error
            return fake(method,path,body)
        waits=[]
        client=RecoveryGenerator('FAKE',config(),Path(folder)/'api_budget_ledger.json',Path(folder)/'calls.jsonl',
            checkpoint=self.checkpoint,confirmed_free_project=True,transport=send,
            now_utc=datetime(2026,11,19,tzinfo=timezone.utc),clock=lambda:0,sleeper=waits.append,jitter=lambda:0)
        client.preflight()
        return client,waits

    def test_checkpoint_reuses_only_valid_note_and_six_prior_requests(self):
        self.assertEqual(self.checkpoint['saved_rows'][0]['judgement']['score'],2)
        self.assertEqual(len(self.checkpoint['saved_rows']),1)
        self.assertEqual(len(self.checkpoint['budget_snapshot']['requests']),6)

    def test_missing_prior_marker_blocks_and_new_marker_is_unique(self):
        with tempfile.TemporaryDirectory() as temp:
            self.setup_drive(temp);path=Path(temp)/'hydrogen_calibration_resume_1.started.json'
            original=path.read_bytes();path.unlink()
            with self.assertRaises(ApiFailure):self.client(temp)
            path.write_bytes(original)
            before={p.name:p.read_bytes() for p in Path(temp).iterdir()}
            register_resume(temp,config(),self.checkpoint)
            with self.assertRaises(FileExistsError):register_resume(temp,config(),self.checkpoint)
            for name,data in before.items():self.assertEqual((Path(temp)/name).read_bytes(),data)

    def test_identical_pending_generation_request(self):
        from final.calibration_final import cases
        from final.judge_final import FinalJudge
        from final.reasoning_calibration import request_seed
        from m3.judge import evidence_payload
        with tempfile.TemporaryDirectory() as temp:
            self.setup_drive(temp);client,_=self.client(temp)
            client.set_request_seed(request_seed('attribution_good',42))
            record=next(c['record'] for c in cases() if c['id']=='attribution_good')
            body=client.request_body(FinalJudge(client).system,json.dumps(evidence_payload(record),ensure_ascii=False))
            self.assertEqual(hashlib.sha256(json.dumps(body,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
                '9f5a82938ae3efda77aea6c6c53045266802da363892446302056361b37ac1b5')
            self.assertEqual(client.cfg['request_timeout_seconds'],180)

    def test_one_503_retry_then_success_and_prior_reservations_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            self.setup_drive(temp);client,waits=self.client(temp,[ApiFailure('api_http_error',503)])
            client.generate('s','u')
            self.assertEqual(client.generation_calls,2);self.assertEqual(client.retry_count,1);self.assertIn(60,waits)
            self.assertEqual(client.ledger.used_or_reserved(),Decimal('3.0940725'))
            ledger=json.loads(client.ledger.path.read_text())
            self.assertEqual(ledger['limit_usd'],'5.00')
            for key,value in self.checkpoint['budget_snapshot']['requests'].items():self.assertEqual(ledger['requests'][key],value)

    def test_two_503_stop_and_keep_both_reservations(self):
        with tempfile.TemporaryDirectory() as temp:
            self.setup_drive(temp);client,_=self.client(temp,[ApiFailure('api_http_error',503)]*2)
            with self.assertRaises(ApiFailure):client.generate('s','u')
            self.assertEqual(client.generation_calls,2);self.assertEqual(client.retry_count,1)
            self.assertEqual(client.ledger.used_or_reserved(),Decimal('3.6994725'))

    def test_timeouts_json_auth_and_quota_are_not_retried(self):
        for code,status in [('api_timeout',None),('api_network_error',None),('api_invalid_json_envelope',200),('api_http_error',401),('api_http_error',429)]:
            with self.subTest(code=code,status=status),tempfile.TemporaryDirectory() as temp:
                self.setup_drive(temp);client,_=self.client(temp,[ApiFailure(code,status)])
                with self.assertRaises(ApiFailure):client.generate('s','u')
                self.assertEqual(client.generation_calls,1);self.assertEqual(client.retry_count,0)

    def test_budget_is_cumulative_and_wrong_score_not_changed(self):
        with tempfile.TemporaryDirectory() as temp:
            self.setup_drive(temp);client,_=self.client(temp,score=4)
            self.assertEqual(json.loads(client.generate('s','u'))['puntaje'],4)
            client.ledger.reserve('2')
            with self.assertRaises(ApiFailure) as exc:client.generate('s','u')
            self.assertEqual(exc.exception.code,'calibration_estimate_budget_exhausted')
            self.assertEqual(client.generation_calls,1)

    def test_runner_reuses_valid_note_stops_after_one_retry_and_preserves_money(self):
        import contextlib,os
        from final import run_hydrogen_recovery11 as runner
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);drive=folder/'drive';drive.mkdir();self.setup_drive(drive)
            client,_=self.client(drive,[ApiFailure('api_http_error',503)]*2)
            result=folder/'results'
            with patch.object(runner,'GeminiRESTGenerator',return_value=client),patch('sys.argv',[
                    'runner','--output',str(result),'--budget-dir',str(drive),'--confirm-free-project']),\
                    patch.dict(os.environ,{'GEMINI_API_KEY':'FAKE','WANDB_API_KEY':''}),contextlib.redirect_stdout(io.StringIO()):
                runner.main()
            meta=json.loads((result/'metadata.json').read_text(encoding='utf-8'))
            rows=[json.loads(s) for s in (result/'raw_judgements.jsonl').read_text(encoding='utf-8').splitlines()]
            self.assertEqual(rows[0]['judgement'],self.checkpoint['saved_rows'][0]['judgement'])
            self.assertEqual(meta['historical_generation_http_calls'],6)
            self.assertEqual(meta['generation_http_calls'],2);self.assertEqual(meta['technical_503_retries_used'],1)
            self.assertEqual(meta['estimated_or_reserved_total_usd'],'3.6994725')
            self.assertFalse(meta['judge_validated_for_final']);self.assertFalse(meta['final_gold_loaded'])
            self.assertTrue((result/'reused_checkpoint.jsonl').is_file())

    def test_real_request_diagnostics_do_not_retain_private_messages(self):
        cases=[(TimeoutError('FAKE_SECRET'),'api_timeout',None),
            (urllib.error.URLError('FAKE_SECRET'),'api_network_error',None),
            (urllib.error.HTTPError('https://example.invalid',503,'FAKE_SECRET',{},io.BytesIO(b'{"error":{"status":"UNAVAILABLE","message":"overloaded FAKE_SECRET"}}')),'api_http_error',503)]
        for error,code,status in cases:
            with self.subTest(code=code),tempfile.TemporaryDirectory() as temp:
                self.setup_drive(temp);client,_=self.client(temp)
                with patch('urllib.request.build_opener') as opener:
                    opener.return_value.open.side_effect=error
                    with self.assertRaises(ApiFailure) as exc:client._request('GET','models/gemini-4-hydrogen')
                self.assertEqual(exc.exception.code,code);self.assertEqual(exc.exception.status,status)
                self.assertNotIn('FAKE_SECRET',(Path(temp)/'calls.jsonl').read_text())
        with tempfile.TemporaryDirectory() as temp:
            self.setup_drive(temp);client,_=self.client(temp)
            with patch('urllib.request.build_opener') as opener:
                response=opener.return_value.open.return_value.__enter__.return_value
                response.status=200;response.read.return_value=b'<html>FAKE_SECRET not JSON</html>'
                with self.assertRaises(ApiFailure) as exc:client._request('GET','models/gemini-4-hydrogen')
            self.assertEqual(exc.exception.code,'api_invalid_json_envelope');self.assertEqual(exc.exception.status,200)
            self.assertNotIn('FAKE_SECRET',(Path(temp)/'calls.jsonl').read_text())

    def test_bad_json_envelope_is_distinct_from_model_grade_format(self):
        with tempfile.TemporaryDirectory() as temp:
            self.setup_drive(temp);client,_=self.client(temp)
            response=MagicMock();response.__enter__.return_value.status=200
            response.__enter__.return_value.read.return_value=b'<html>FAKE_SECRET</html>'
            with patch('urllib.request.build_opener') as opener:
                opener.return_value.open.return_value=response
                with self.assertRaises(ApiFailure) as exc:client._request('GET','models/gemini-4-hydrogen')
            self.assertEqual(exc.exception.code,'api_invalid_json_envelope');self.assertEqual(exc.exception.status,200)
            self.assertNotIn('FAKE_SECRET',(Path(temp)/'calls.jsonl').read_text())
