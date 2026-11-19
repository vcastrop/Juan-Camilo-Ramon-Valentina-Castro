import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from final import human_closure_receipt as closure
from final.prepare_product_judge_plan import plan

ROOT = Path(__file__).resolve().parents[2]


class HumanClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (ROOT/'final/evidence/human_closure_19/original_judge_review.md').read_text(encoding='utf-8')

    def test_actual_conditional_acceptance_retains_original_doubt(self):
        result = closure.judge_receipt(self.text)
        row = result['decisions']['confirm_empty_bad']
        self.assertEqual(row['declared_decision'], 'DUDOSO')
        self.assertEqual(row['effective_decision'], 'SI')
        self.assertEqual(row['resolution'], 'explicit_user_conditional_acceptance_verified')
        self.assertTrue(result['judge_validated_for_task_after_technical_gates'])
        self.assertFalse(result['raw_judge_scores_adjusted'])

    def test_doubt_without_explicit_conditional_acceptance_stays_open(self):
        text = self.text.replace('Si la rúbrica la contiene, el motivo es aceptable (SI).', 'Necesito revisarlo.')
        result = closure.judge_receipt(text)
        self.assertEqual(result['decisions']['confirm_empty_bad']['effective_decision'], 'DUDOSO')
        self.assertFalse(result['judge_validated_for_task_after_technical_gates'])

    def test_condition_not_met_is_not_approved(self):
        with patch.dict(closure.RUBRIC, {2: 'Un texto sin ese tope.'}):
            result = closure.judge_receipt(self.text)
        self.assertFalse(result['judge_validated_for_task_after_technical_gates'])

    def test_additional_calibration_doubt_not_silently_approved(self):
        result = closure.judge_receipt(self.text.replace('Hay tres salvedades:', 'Hay tres salvedades. Otro caso DUDOSO:'))
        self.assertFalse(result['judge_validated_for_task_after_technical_gates'])

    def test_unsigned_or_duplicate_section_rejected(self):
        with self.assertRaises(ValueError): closure.judge_receipt(self.text.replace('Revisor/a: Juan Camilo Ramon Perez', 'Revisor/a: PENDIENTE'))
        with self.assertRaises(ValueError): closure.judge_receipt(self.text+'\n## confirm_field_good\nMotivo aceptable: SI\n')

    def test_eight_doubts_closed_without_rewriting_prior_review(self):
        path = ROOT/'final/evidence/human_response_review_01/parsed_review.json'
        original = path.read_bytes()
        result = closure.receive_closure(ROOT)
        domain = result['domain_closure']
        self.assertEqual(len(domain['changes']), 11)
        self.assertEqual(domain['summary']['records_with_doubts'], 0)
        self.assertTrue(domain['summary']['nf4_deployment_veto'])
        self.assertEqual(len(domain['summary']['human_control_regressions']), 2)
        self.assertIsNone(domain['summary']['domain_rate'])
        self.assertTrue(domain['summary']['judge_validated'])
        self.assertFalse(domain['summary']['judge_grades_available'])
        self.assertEqual(path.read_bytes(), original)
        self.assertFalse(result['product_scores_created'])

    def test_product_plan_keeps_all_rows_and_no_gold_or_dispatch(self):
        result = plan(ROOT)
        self.assertEqual(len(result['jobs']), 110)
        for profile in result['profiles']:
            self.assertEqual(sum(j['profile'] == profile for j in result['jobs']), 22)
        self.assertTrue(all(j['judgement'] is None for j in result['jobs']))
        self.assertTrue(all('expected' not in j['judge_payload'] and 'group' not in j['judge_payload'] for j in result['jobs']))
        self.assertEqual(sum(j['judge_payload']['respuesta_propuesta'] is None for j in result['jobs']), 7)
        self.assertFalse(result['paid_dispatch_authorized'])
        self.assertEqual(result['current_authorized_total_usd'], '5.00')
