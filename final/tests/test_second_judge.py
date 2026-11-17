import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

from final.run_second_judge import verify_second_config
from final.calibration_final import cases as regression_cases,summarize as summarize_regression
from final.confirmation_final import cases as confirmation_cases,summarize as summarize_confirmation

ROOT=Path(__file__).resolve().parents[2]


class SecondJudgeTests(unittest.TestCase):
    def test_original_qwen_failure_is_preserved_not_relabelled(self):
        with zipfile.ZipFile(ROOT/'final/evidence/judge_calibration_01/original_results.zip') as z:
            rows=[json.loads(s) for s in z.read('raw_judgements.jsonl').decode().splitlines()]
            saved=json.loads(z.read('calibration_summary.json'))
        self.assertEqual(summarize_regression(rows),saved)
        self.assertFalse(saved['gate_passed'])
        self.assertEqual(saved['orientation_matches'],15)
        self.assertIn('empty_explanation_bad',saved['bad_accepted'])
        self.assertTrue(all(r['judgement']['score_adjusted'] is False for r in rows))

    def test_only_second_model_changes_not_shared_parameters(self):
        new=json.loads((ROOT/'final/judge_second_config.json').read_text(encoding='utf-8'))
        old=json.loads((ROOT/'final/judge_calibration_config.json').read_text(encoding='utf-8'))
        verify_second_config(new,old)
        changed=copy.deepcopy(new);changed['max_new_tokens']=640
        with self.assertRaises(ValueError):verify_second_config(changed,old)
        changed=copy.deepcopy(new);changed['acceptance_rules_changed']=True
        with self.assertRaises(ValueError):verify_second_config(changed,old)

    def test_confirmation_separate_and_preparation_does_not_claim_inference(self):
        items=confirmation_cases()
        self.assertEqual(len(items),12)
        self.assertFalse({c['id'] for c in items}&{c['id'] for c in regression_cases()})
        self.assertNotIn('CO1.PCCNTR',json.dumps(items))
        meta=json.loads((ROOT/'final/eval/confirmation_v1/metadata.json').read_text(encoding='utf-8'))
        self.assertFalse(meta['model_inference_performed'])

    def ideal_confirmation(self):
        return [{'id':c['id'],'judgement':{'score':5 if c['group']=='good' else 1}} for c in confirmation_cases()]

    def test_confirmation_ideal_gate_is_not_final_validation(self):
        summary=summarize_confirmation(self.ideal_confirmation())
        self.assertTrue(summary['gate_passed'])
        self.assertFalse(summary['judge_validated_for_final'])
        self.assertTrue(summary['human_semantic_audit_required'])

    def test_new_bad_high_score_blocks_confirmation(self):
        rows=self.ideal_confirmation()
        next(r for r in rows if r['id']=='confirm_empty_bad')['judgement']['score']=5
        self.assertFalse(summarize_confirmation(rows)['gate_passed'])

    def test_confirmation_duplicate_missing_or_boolean_score_fails(self):
        rows=self.ideal_confirmation();rows[-1]=rows[-2]
        self.assertFalse(summarize_confirmation(rows)['gate_passed'])
        rows=self.ideal_confirmation();rows[0]['judgement']['score']=True
        self.assertFalse(summarize_confirmation(rows)['gate_passed'])

    def test_second_runner_no_secret_stops_before_loading_model(self):
        with tempfile.TemporaryDirectory() as temp:
            env=dict(os.environ);env.pop('WANDB_API_KEY',None)
            output=Path(temp)/'results'
            proc=subprocess.run([sys.executable,str(ROOT/'final/run_second_judge.py'),'--output',str(output),'--require-wandb'],
                                env=env,cwd=ROOT,capture_output=True,text=True)
            self.assertNotEqual(proc.returncode,0)
            meta=json.loads((output/'metadata.json').read_text(encoding='utf-8'))
            self.assertEqual(meta['status'],'failed')
            self.assertNotIn('load_seconds',meta)
            self.assertFalse(meta['confirmation_executed'])
            self.assertFalse(meta['judge_validated_for_final'])

    def test_second_notebook_compiles_and_does_not_run_confirmation(self):
        nb=json.loads((ROOT/'final/ContractRisk_Final_Juez_02_Mistral_Colab.ipynb').read_text(encoding='utf-8'))
        source=''
        for cell in nb['cells']:
            if cell['cell_type']=='code':
                compile(cell['source'],'cell','exec');source+=cell['source']
        self.assertIn('final/run_second_judge.py',source)
        self.assertNotIn('confirmation_final',source)
