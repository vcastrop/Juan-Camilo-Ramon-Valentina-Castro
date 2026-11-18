import json
from pathlib import Path
import unittest

from final.judge_criteria import CriteriaJudge,parse_final
from final.reasoning_generator import extract_final_ids,encode_reasoning_chat
from final.reasoning_calibration import request_seed,pilot_summary,full_summary,validate_config
from final.calibration_final import cases,schedule


def verdict(score=5,**changes):
    checks={'respuesta':'respaldada','explicacion':'respaldada','citas':'respaldan','abstencion':'no_aplica','acusacion':'ausente_o_negada'}
    checks.update(changes)
    return json.dumps({'verificaciones':checks,'puntaje':score,'razon':'Synthetic evidence statement'},ensure_ascii=False)


class FakeGenerator:
    def __init__(self,outputs,generation=None):
        self.outputs=iter(outputs);self.calls=[];self.last_generation=generation or {'thinking_closed':True,'reached_token_limit':False}
    def generate(self,system,user):self.calls.append(json.loads(user));return next(self.outputs)


class ReasoningJudgeTests(unittest.TestCase):
    def test_score_not_clamped_or_semantically_retried(self):
        record=next(c['record'] for c in cases() if c['id']=='empty_explanation_bad')
        gen=FakeGenerator([verdict(5,explicacion='ausente')])
        result=CriteriaJudge(gen).evaluate(record)
        self.assertEqual(result['score'],5)
        self.assertTrue(result['internal_inconsistencies'])
        self.assertFalse(result['score_adjusted'])
        self.assertEqual(len(gen.calls),1)

    def test_no_gold_or_expected_range_in_payload(self):
        record=dict(cases()[0]['record'],expected='never send',expected_score_range=[4,5],correct=True)
        gen=FakeGenerator([verdict()]);CriteriaJudge(gen).evaluate(record)
        self.assertNotIn('expected',gen.calls[0])
        self.assertNotIn('correct',gen.calls[0])
        self.assertNotIn('expected_score_range',gen.calls[0])

    def test_only_final_format_failure_gets_one_retry(self):
        gen=FakeGenerator(['not json',verdict(2,explicacion='contradicha')])
        result=CriteriaJudge(gen).evaluate(cases()[0]['record'])
        self.assertEqual(result['score'],2)
        self.assertEqual(len(gen.calls),2)

    def test_incomplete_thinking_or_budget_not_retried(self):
        for generation in [{'thinking_closed':False},{'thinking_closed':True,'reached_token_limit':True}]:
            gen=FakeGenerator([''],generation=generation)
            result=CriteriaJudge(gen).evaluate(cases()[0]['record'])
            self.assertIsNone(result['score'])
            self.assertEqual(len(gen.calls),1)

    def test_final_extraction_never_searches_reasoning_for_json(self):
        ids,meta=extract_final_ids([11,22,33],999)
        self.assertIsNone(ids)
        self.assertFalse(meta['thinking_closed'])
        ids,meta=extract_final_ids([11,22,999,44,55],999)
        self.assertEqual(ids,[44,55])
        self.assertTrue(meta['thinking_closed'])
        self.assertNotIn('thinking_text',meta)
        self.assertIsNone(extract_final_ids([999,11,999,44],999)[0])

    def test_bad_schemas_and_boolean_score_rejected(self):
        obj=json.loads(verdict());obj['puntaje']=True
        with self.assertRaises(ValueError):parse_final(json.dumps(obj))
        obj=json.loads(verdict());obj['verificaciones']['citas']='unknown'
        with self.assertRaises(ValueError):parse_final(json.dumps(obj))

    def test_native_reasoning_switch_used_both_paths(self):
        class Tokenizer:
            def apply_chat_template(self,messages,tokenize=False,**kwargs):
                assert kwargs['enable_thinking'] is True
                return [1,2,3] if tokenize else 'chat'
            def __call__(self,text,add_special_tokens=True):
                assert add_special_tokens is False
                return {'input_ids':[1,2,3]}
        _,audit=encode_reasoning_chat(Tokenizer(),'s','u')
        self.assertTrue(audit['native_equivalent'])

    def test_seed_stable_per_anchor_not_length(self):
        self.assertEqual(request_seed('short_good'),request_seed('short_good'))
        self.assertNotEqual(request_seed('short_good'),request_seed('number_bad'))

    def ideal_rows(self):
        by_id={c['id']:c for c in cases()}
        rows=[]
        for condition,cid in schedule():
            good=by_id[cid]['group']=='good'
            checks={'respuesta':'respaldada' if good else 'contradicha','explicacion':'respaldada' if good else 'contradicha',
                    'citas':'respaldan' if good else 'no_respaldan','abstencion':'justificada' if good and by_id[cid]['record']['output']['abstencion'] else 'no_aplica',
                    'acusacion':'ausente_o_negada'}
            if not by_id[cid]['record']['output']['explicacion']:checks['explicacion']='ausente'
            rows.append({'condition':condition,'id':cid,'judgement':{'score':5 if good else 1,'checks':checks,'internal_inconsistencies':[]}})
        return rows

    def test_pilot_missing_cases_not_labelled_as_executed_failures(self):
        rows=self.ideal_rows()[:1]
        summary=pilot_summary(rows,['short_good','short_bad'])
        self.assertFalse(summary['pilot_passed'])
        self.assertEqual(summary['unexecuted_ids'],['short_bad'])
        self.assertEqual(summary['failed_ids'],[])

    def test_full_gate_never_accepts_inconsistency_or_skips_original_thresholds(self):
        rows=self.ideal_rows()
        self.assertTrue(full_summary(rows)['gate_passed'])
        rows[0]['judgement']['internal_inconsistencies']=['contradiction']
        self.assertFalse(full_summary(rows)['gate_passed'])
        rows=self.ideal_rows();rows[1]['judgement']['score']=5
        self.assertFalse(full_summary(rows)['gate_passed'])

    def test_actual_tokenizer_evidence_not_new_model_judgement(self):
        root=Path(__file__).resolve().parents[2]
        proof=json.loads((root/'final/evidence/reasoning_tokenizer_cpu/diagnostic.json').read_text(encoding='utf-8'))
        self.assertEqual(proof['native_matches'],38)
        self.assertEqual(proof['mode_switch_matches'],38)
        self.assertFalse(proof['model_inference_performed'])
        self.assertFalse(proof['gpu_used'])

    def test_fixed_sampling_and_pilot_not_silently_changed(self):
        root=Path(__file__).resolve().parents[2]
        config=json.loads((root/'final/judge_reasoning_config.json').read_text(encoding='utf-8'))
        validate_config(config)
        config['do_sample']=False
        with self.assertRaises(ValueError):validate_config(config)
