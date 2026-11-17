import copy
import json
import unittest
from final.efficiency_acceptance import assess, policy_fingerprint, POLICY_PATH


def synthetic_profile(n=20):
    return {**{key:'a'*64 for key in ['eval_set_sha256','harness_sha256','judge_config_sha256','judge_calibration_sha256','shared_inference_config_sha256']},
            'policy_sha256':policy_fingerprint(json.loads(POLICY_PATH.read_text(encoding='utf-8'))),
            'judge_calibration_passed':True,'hardware_fingerprint':{'device':'synthetic fixture'},'profile':'fp16',
            'rows':[{'id':str(i),'domain_pass':True,'critical_failures':[],
                     'controls':{'abstention':True,'adversarial':True,'invariance':True},
                     'peak_cuda_allocated_bytes':1000,'wall_seconds':1.} for i in range(n)]}


class EfficiencyAcceptanceTests(unittest.TestCase):
    def pair(self,n=20):
        before=synthetic_profile(n);after=copy.deepcopy(before)
        after.update(profile='nf4_generator',quantization_verified=True)
        for row in after['rows']: row['peak_cuda_allocated_bytes']=800
        return before,after

    def test_exact_boundaries_pass(self):
        before,after=self.pair()
        after['rows'][0]['domain_pass']=False
        result=assess(before,after)
        self.assertTrue(result['accepted'])
        self.assertEqual(result['domain_drop_percentage_points'],5.)

    def test_five_points_not_relative_five_percent(self):
        before,after=self.pair()
        for row in before['rows'][:4]:row['domain_pass']=False
        after['rows']=copy.deepcopy(before['rows'])
        for row in after['rows']:row['peak_cuda_allocated_bytes']=800
        after['rows'][4]['domain_pass']=False
        self.assertTrue(assess(before,after)['accepted']) # 80% -> 75%

    def test_one_case_in_nineteen_exceeds_five_points(self):
        before,after=self.pair(19);after['rows'][0]['domain_pass']=False
        self.assertIn('domain_drop_exceeds_limit',assess(before,after)['reasons'])

    def test_memory_under_twenty_percent_fails(self):
        before,after=self.pair();after['rows'][0]['peak_cuda_allocated_bytes']=801
        self.assertIn('insufficient_memory_reduction',assess(before,after)['reasons'])

    def test_critical_regression_not_hidden_by_average(self):
        before,after=self.pair()
        before['rows'][0]['critical_failures']=['wrong_amount']
        after['rows'][1]['critical_failures']=['wrong_amount']
        self.assertIn('new_critical_failures',assess(before,after)['reasons'])

    def test_each_control_cannot_regress(self):
        before,after=self.pair();after['rows'][2]['controls']['invariance']=False
        self.assertIn('control_regressions',assess(before,after)['reasons'])

    def test_different_hardware_or_gold_not_evaluable(self):
        for key,value in [('hardware_fingerprint',{'device':'different'}),('eval_set_sha256','b'*64)]:
            before,after=self.pair();after[key]=value
            self.assertEqual(assess(before,after)['status'],'not_evaluable')

    def test_uncalibrated_judge_not_evaluable(self):
        before,after=self.pair();before['judge_calibration_passed']=False
        self.assertEqual(assess(before,after)['status'],'not_evaluable')

    def test_unknown_result_or_missing_case_not_accepted(self):
        before,after=self.pair();after['rows'][0]['domain_pass']=None
        self.assertFalse(assess(before,after)['accepted'])
        before,after=self.pair();after['rows'].pop()
        self.assertFalse(assess(before,after)['accepted'])

    def test_duplicate_ids_and_nan_rejected(self):
        before,after=self.pair();after['rows'][1]['id']='0'
        self.assertFalse(assess(before,after)['accepted'])
        before,after=self.pair();after['rows'][0]['wall_seconds']=float('nan')
        self.assertFalse(assess(before,after)['accepted'])

    def test_no_quantization_confirmation_no_acceptance(self):
        before,after=self.pair();after['quantization_verified']=False
        self.assertFalse(assess(before,after)['accepted'])

    def test_predeclared_policy_cannot_be_substituted(self):
        before,after=self.pair()
        before['policy_sha256']=after['policy_sha256']='b'*64
        self.assertEqual(assess(before,after)['status'],'not_evaluable')

    def test_missing_control_categories_cannot_pass(self):
        before,after=self.pair()
        for profile in [before,after]:
            for row in profile['rows']:row['controls']={}
        self.assertEqual(assess(before,after)['status'],'not_evaluable')
