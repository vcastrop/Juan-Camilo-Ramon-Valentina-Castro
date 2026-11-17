import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from final.visual_probe import load_inputs
from final.score_visual_probe import diagnose, percentile

PACK = Path(__file__).resolve().parents[1]/'eval/visual_candidates_v1'


class VisualProbeTests(unittest.TestCase):
    def cases(self):
        return (json.loads((PACK/'manifest.json').read_text(encoding='utf-8')),
                json.loads((PACK/'references_for_human_review.json').read_text(encoding='utf-8')))

    def mock_rows(self):
        cases, refs = self.cases()
        return [{'id':c['id'], 'wall_seconds':1., 'result':{
            'visual':{'output':r['expected_visual_fields'], 'parse_error':None},
            'output':{'respuesta':f"{r['expected_visual_fields']['modalidad']} {r['expected_visual_fields']['valor_cop']} COP",
                      'abstencion':r['expected_abstention'], 'citas':['IMAGE::input']},
            'contexts':[{'chunk_id':'IMAGE::input'}]}} for c,r in zip(cases,refs)]

    def test_review_hashes(self):
        approval=json.loads((PACK/'human_approval.json').read_text(encoding='utf-8'))
        for name,key in [('manifest.json','manifest_sha256'),('references_for_human_review.json','references_sha256'),('metadata.json','metadata_sha256')]:
            self.assertEqual(hashlib.sha256((PACK/name).read_bytes()).hexdigest(),approval[key])

    def test_inference_inputs_do_not_require_reference_file(self):
        with tempfile.TemporaryDirectory() as temp:
            pack=Path(temp)
            (pack/'x.png').write_bytes(b'fixture')
            cases=[{'id':'a','question':'q','image':'x.png','sha256':hashlib.sha256(b'fixture').hexdigest()}]
            (pack/'manifest.json').write_text(json.dumps(cases),encoding='utf-8')
            (pack/'human_approval.json').write_text(json.dumps({'approved_ids':['a'], 'manifest_sha256':hashlib.sha256((pack/'manifest.json').read_bytes()).hexdigest()}),encoding='utf-8')
            self.assertEqual(set(load_inputs(pack)[0]),{'id','question','path'})
            (pack/'x.png').write_bytes(b'changed')
            with self.assertRaises(ValueError): load_inputs(pack)

    def test_synthetic_correct_diagnostic(self):
        cases,refs=self.cases()
        details,summary=diagnose(cases,refs,self.mock_rows())
        self.assertEqual(summary['literal_response_proxy_count'],10)
        self.assertEqual(summary['exact_extraction_count'],10)
        self.assertFalse(summary['quality_approved'])
        self.assertTrue(all(p['both_response_proxies_pass'] for p in summary['pairs']))

    def test_no_prefix_number_or_unknown_citation_credit(self):
        cases,refs=self.cases(); rows=self.mock_rows()
        rows[0]['result']['output']['respuesta']='Mínima cuantía 606007500 COP'
        rows[1]['result']['output']['citas']=['invented']
        details,_=diagnose(cases,refs,rows)
        self.assertFalse(details[0]['value_literal_present'])
        self.assertFalse(details[1]['image_citation_valid'])

    def test_missing_rows_stay_in_denominator(self):
        cases,refs=self.cases()
        _,summary=diagnose(cases,refs,[])
        self.assertEqual(summary['expected_count'],10)
        self.assertEqual(summary['literal_response_proxy_count'],0)
        self.assertEqual(summary['exact_extraction_count'],0)
        self.assertIsNone(summary['observed_wall_p95_seconds'])

    def test_ambiguous_or_duplicate_rows_rejected(self):
        cases,refs=self.cases(); rows=self.mock_rows()
        with self.assertRaises(ValueError): diagnose(cases,refs,rows+[rows[0]])

    def test_percentile(self):
        self.assertEqual(percentile([4,1,3,2],.5),2.5)
        self.assertAlmostEqual(percentile([1,2],.95),1.95)

    def test_missing_secret_stops_before_model_load_and_preserves_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/'results'
            env=dict(os.environ)
            env.pop('WANDB_API_KEY',None)
            root=PACK.parents[2]
            proc=subprocess.run([sys.executable,str(root/'final/visual_probe.py'),'--output',str(output),'--require-wandb'],
                                cwd=root,env=env,capture_output=True,text=True)
            self.assertNotEqual(proc.returncode,0)
            meta=json.loads((output/'metadata.json').read_text(encoding='utf-8'))
            self.assertEqual(meta['status'],'failed')
            self.assertEqual(meta['wandb_status'],'disabled')
            self.assertNotIn('load_seconds',meta)
            self.assertFalse((output/'predictions.jsonl').exists())
