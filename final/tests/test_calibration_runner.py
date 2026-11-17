import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from final.run_judge_calibration import verify_review,main
from final.generators import CausalGenerator
from final.prepare_eval_final import canonical_hash
from final.calibration_final import cases,ACCEPTANCE
from final.judge_final import rubric_fingerprint

ROOT=Path(__file__).resolve().parents[2]


class CalibrationRunnerTests(unittest.TestCase):
    def test_missing_human_review_blocks_before_wandb_and_model(self):
        # A missing approval must block even after the real project review is later completed.
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/'run'
            with patch.object(sys,'argv',['run_judge_calibration.py','--output',str(output)]), \
                 patch('final.run_judge_calibration.verify_review',side_effect=ValueError('Missing review')), \
                 self.assertRaises(ValueError):
                main()
            meta=json.loads((output/'metadata.json').read_text(encoding='utf-8'))
            self.assertEqual(meta['status'],'blocked_pending_human_review')
            self.assertNotIn('load_seconds',meta)
            self.assertFalse(meta['judge_validated_for_final'])

    def test_review_hash_change_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            pack=Path(temp)
            for name,data in [('anchors.json',cases()),('rules.json',ACCEPTANCE)]:
                (pack/name).write_text(json.dumps(data),encoding='utf-8')
            approval={'status':'approved','approved_ids':[c['id'] for c in cases()],
                      'anchors_canonical_sha256':canonical_hash(cases()),'rules_canonical_sha256':canonical_hash(ACCEPTANCE),
                      'rubric_sha256':rubric_fingerprint(),
                      'judge_config_canonical_sha256':canonical_hash(json.loads((ROOT/'final/judge_calibration_config.json').read_text(encoding='utf-8')))}
            (pack/'human_approval.json').write_text(json.dumps(approval),encoding='utf-8')
            verify_review(pack)
            changed=cases();changed[0]['expected_score_range']=[1,2]
            (pack/'anchors.json').write_text(json.dumps(changed),encoding='utf-8')
            with self.assertRaises(ValueError):verify_review(pack)

    def mocks(self,loaded=True,device='cuda'):
        class Layer4bit:pass
        model=SimpleNamespace(is_loaded_in_4bit=loaded,eval=lambda: model,
                              modules=lambda:[Layer4bit()],parameters=lambda:[SimpleNamespace(device=SimpleNamespace(type=device))])
        calls=[]
        def load(*args,**kwargs):calls.append(kwargs);return model
        transformers=SimpleNamespace(AutoTokenizer=SimpleNamespace(from_pretrained=lambda *a,**k:object()),
                                     AutoModelForCausalLM=SimpleNamespace(from_pretrained=load),
                                     BitsAndBytesConfig=lambda **kwargs:kwargs)
        torch=SimpleNamespace(float16='float16-marker',cuda=SimpleNamespace(is_available=lambda:True))
        return {'torch':torch,'transformers':transformers,'bitsandbytes.nn':SimpleNamespace(Linear4bit=Layer4bit)},calls

    def test_fake_quantized_loader_uses_pinned_nf4_no_to_or_auto(self):
        modules,calls=self.mocks()
        with patch.dict(sys.modules,modules):gen=CausalGenerator('synthetic','revision',precision='nf4')
        self.assertEqual(calls[0]['revision'],'revision')
        self.assertEqual(calls[0]['device_map'],{'':0})
        self.assertEqual(calls[0]['quantization_config']['bnb_4bit_quant_type'],'nf4')
        self.assertEqual(calls[0]['quantization_config']['bnb_4bit_compute_dtype'],'float16-marker')
        self.assertTrue(gen.load_settings['quantization_verified'])

    def test_fake_model_cannot_silently_remain_fp16(self):
        modules,_=self.mocks(loaded=False)
        with patch.dict(sys.modules,modules),self.assertRaises(RuntimeError):
            CausalGenerator('synthetic','revision',precision='nf4')

    def test_fake_cpu_offload_rejected(self):
        modules,_=self.mocks(device='cpu')
        with patch.dict(sys.modules,modules),self.assertRaises(RuntimeError):
            CausalGenerator('synthetic','revision',precision='nf4')
