import copy
import contextlib
from datetime import datetime,timezone
from decimal import Decimal
import json
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from final.evaluation21 import plan,make_jobs
from final.run_evaluation21 import register,EvaluationGenerator,financial_checkpoint,summary,MARKER
from final.product_judge14 import POLICY
from final.confirmation13_receipt import SHA13
from final.prepare_eval_final import canonical_hash
from final.api_budget7 import BudgetLedger7
from final.gemini_judge_client import ApiFailure
from final.tests.test_hydrogen_judge import config,Transport

ROOT=Path(__file__).resolve().parents[2]


class Evaluation21Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=plan()
        cls.ledger,cls.meta=financial_checkpoint()

    def drive(self,folder):
        with zipfile.ZipFile(ROOT/'final/evidence/product_14/original_results.zip') as z:
            for name in ['api_budget_authorization_usd7.json','api_budget_ledger_before_usd7.json']:
                (folder/name).write_bytes(z.read(name))
            (folder/'api_budget_ledger.json').write_bytes(z.read('budget_ledger_snapshot.json'))
        (folder/'product_judge_14.started.json').write_text(json.dumps({'policy':POLICY,'checkpoint_sha256':SHA13}),encoding='utf-8')

    def client(self,folder,error=None):
        fake=Transport(score=2,error=error)
        def send(method,path,body):
            return self.meta['model_preflight'] if method=='GET' else fake(method,path,body)
        return EvaluationGenerator('FAKE_NOT_A_REAL_KEY',config(),folder/'api_budget_ledger.json',folder/'events.jsonl',
            checkpoint={'metadata':self.meta},plan_sha256=canonical_hash(self.p),
            confirmed_paid_project=True,confirmed_total_usd7=True,exclusive_project_use=True,
            transport=send,now_utc=datetime(2026,11,20,tzinfo=timezone.utc),clock=lambda:0,sleeper=lambda n:None)

    def test_fourteen_notes_but_only_twelve_human_transfers(self):
        jobs=self.p['jobs']
        self.assertEqual(sum(j['judgement'] is not None for j in jobs),14)
        self.assertEqual(sum(j['human_transfer'] is not None for j in jobs),12)
        self.assertTrue(all(j['human_transfer'] is None for j in jobs if j['id'].startswith('vis_')))

    def test_known_bad_note_and_human_decision_not_promoted(self):
        job=next(j for j in self.p['jobs'] if j['id']=='m3_009')
        self.assertEqual(job['judgement']['score'],2)
        self.assertFalse(job['human_transfer']['domain_pass'])

    def test_no_gold_or_profile_in_judge_payload(self):
        for job in self.p['jobs']:
            self.assertEqual(set(job['judge_payload']),{'pregunta','respuesta_propuesta','fragmentos','calculos_verificables'})
        self.assertEqual(len(self.p['new_judge_ids']),8)
        self.assertFalse(summary(self.p['jobs'])['complete'])
        self.assertIsNone(summary(self.p['jobs'])['judge_mean_1_5'])

    def test_marker_prevents_repeat_without_changing_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);self.drive(folder)
            register(folder,self.p)
            with self.assertRaises(FileExistsError):register(folder,self.p)
            data=json.loads((folder/'api_budget_ledger.json').read_text())
            self.assertEqual(data,self.ledger)

    def test_wrong_ledger_never_reset(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);self.drive(folder)
            data=copy.deepcopy(self.ledger);data['requests']['other']={'status':'reserved_before_dispatch','charged_or_reserved_usd':'0.1','worst_case_usd':'0.1'}
            path=folder/'api_budget_ledger.json';path.write_text(json.dumps(data))
            with self.assertRaises(ValueError):register(folder,self.p)
            self.assertEqual(json.loads(path.read_text()),data)

    def test_new_note_preserves_prior167_and_cumulative_cap(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);self.drive(folder);register(folder,self.p)
            client=self.client(folder);client.preflight();client.generate('test system','test user')
            data=json.loads((folder/'api_budget_ledger.json').read_text())
            self.assertEqual(len(data['requests']),168)
            self.assertTrue(all(data['requests'][k]==v for k,v in self.ledger['requests'].items()))
            events=[json.loads(s) for s in (folder/'events.jsonl').read_text().splitlines()]
            self.assertTrue(all(e['protocol']=='ocr-evaluation-21' for e in events))
            self.assertTrue(all(e['free_project_attested'] is False for e in events))
            self.assertLessEqual(client.ledger.used_or_reserved(),Decimal('7.00'))

    def test_provider503_not_retried_or_refunded(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);self.drive(folder);register(folder,self.p)
            client=self.client(folder,ApiFailure('api_http_error',503));client.preflight()
            with self.assertRaises(ApiFailure):client.generate('test system','test user')
            self.assertEqual(client.generation_calls,1)
            self.assertEqual(client.ledger.used_or_reserved(),Decimal('5.7954525')+Decimal('0.6144'))

    def test_full_stage_dispatches_only_eight_and_preserves_fourteen(self):
        from final.run_evaluation21 import run
        fake=Transport(score=2)
        def send(method,path,body):return self.meta['model_preflight'] if method=='GET' else fake(method,path,body)
        def factory(*args,**kwargs):
            return EvaluationGenerator(*args,**kwargs,transport=send,now_utc=datetime(2026,11,20,tzinfo=timezone.utc),
                                       clock=lambda:0,sleeper=lambda n:None)
        class FrozenDate(datetime):
            @classmethod
            def now(cls,tz=None):return datetime(2026,11,20,tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as tmp,patch.dict('os.environ',{'GEMINI_API_KEY':'FAKE_TEST_ONLY'}), \
             patch('final.run_evaluation21.EvaluationGenerator',side_effect=factory), \
             patch('final.run_evaluation21.datetime',FrozenDate),contextlib.redirect_stdout(io.StringIO()):
            folder=Path(tmp);budget=folder/'budget';budget.mkdir();self.drive(budget)
            result=run(folder/'results',budget,confirmed=True)
            self.assertEqual(result['status'],'completed_22_judgements_human_review_pending')
            self.assertEqual(result['generation_http_calls'],8)
            rows=json.loads((folder/'results/combined_judgements.json').read_text(encoding='utf-8'))
            self.assertEqual(sum(r['judge_provenance']=='new_judgement_21' for r in rows),8)
            for before,after in zip(self.p['jobs'],rows):
                if before['judge_provenance']=='exact_packet_transfer_product14':
                    self.assertEqual(before['judgement'],after['judgement'])
            self.assertTrue(result['prior_167_entries_unchanged'])
            self.assertLessEqual(Decimal(result['estimated_or_reserved_total_usd']),Decimal('7'))


if __name__=='__main__':unittest.main()
