import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
from contextlib import nullcontext
import unittest
import numpy as np

from final.chat_encoding import encode_chat
from final.generators import CausalGenerator,NativeChatGenerator
from final.run_mistral_tokenfix import verify_reference,verify_preflight
from final.tokenization_preflight import check_inputs
from final.calibration_final import schedule

ROOT=Path(__file__).resolve().parents[2]


class Encoded(dict):
    def to(self,device):self.device=device;return self


class FakeTokenizer:
    bos_token_id=1
    eos_token_id=2
    def __init__(self):self.calls=[]
    def apply_chat_template(self,messages,tokenize=False,add_generation_prompt=True):
        self.messages=messages
        return [1,3,9] if tokenize else '<s>[INST]sample[/INST]'
    def __call__(self,text,add_special_tokens=True,return_tensors=None):
        self.calls.append(add_special_tokens)
        ids=([1] if add_special_tokens else [])+[1,3,9]
        return Encoded(input_ids=np.array([ids]) if return_tensors else ids)
    def decode(self,tokens,skip_special_tokens=True):
        assert list(tokens)==[99,2]
        return '{"puntaje":5,"razon":"synthetic"}'


class ChatEncodingTests(unittest.TestCase):
    def test_no_additional_bos_and_exact_native_equivalence(self):
        tokenizer=FakeTokenizer()
        self.assertEqual(tokenizer('legacy')['input_ids'][:2],[1,1])
        encoded,audit=encode_chat(tokenizer,'s','u')
        self.assertEqual(encoded['input_ids'],[1,3,9])
        self.assertFalse(tokenizer.calls[-1])
        self.assertEqual(audit['leading_bos_count'],1)
        self.assertTrue(audit['native_equivalent'])

    def test_mismatch_fails_closed(self):
        class Broken(FakeTokenizer):
            def __call__(self,*args,**kwargs):return Encoded(input_ids=[123,456])
        with self.assertRaises(ValueError):encode_chat(Broken(),'s','u')

    def test_native_generator_preserves_loader_and_generation_parameters(self):
        self.assertIs(NativeChatGenerator.__init__,CausalGenerator.__init__)
        gen=NativeChatGenerator.__new__(NativeChatGenerator)
        gen.tokenizer=FakeTokenizer();gen.max_new_tokens=320
        gen.torch=SimpleNamespace(inference_mode=lambda:nullcontext())
        calls=[]
        def generate(**kwargs):calls.append(kwargs);return np.array([[1,3,9,99,2]])
        gen.model=SimpleNamespace(config=SimpleNamespace(max_position_embeddings=2048),
                                  generation_config=SimpleNamespace(eos_token_id=2),generate=generate)
        self.assertIn('puntaje',gen.generate('system','user'))
        self.assertEqual(calls[0]['max_new_tokens'],320)
        self.assertIs(calls[0]['do_sample'],False)
        self.assertEqual(calls[0]['pad_token_id'],2)
        self.assertEqual(gen.last_generation['input_tokens'],3)
        self.assertEqual(gen.last_generation['output_tokens'],2)
        self.assertTrue(gen.last_generation['chat_encoding']['native_equivalent'])

    def test_real_cpu_diagnostic_not_model_improvement(self):
        proof=json.loads((ROOT/'final/evidence/tokenization_cpu_01/diagnostic.json').read_text(encoding='utf-8'))
        self.assertFalse(proof['model_inference_performed'])
        by_model={r['model']:r for r in proof['models']}
        mistral=by_model['mistralai/Mistral-7B-Instruct-v0.3']
        qwen=by_model['Qwen/Qwen2.5-7B-Instruct']
        self.assertEqual(mistral['legacy_native_mismatches'],38)
        self.assertEqual(mistral['corrected_native_matches'],38)
        self.assertEqual(qwen['legacy_native_mismatches'],0)

    def test_preflight_checks_every_original_input_length(self):
        old=[{'condition':condition,'id':cid,'judgement':{'attempts':[{'generation':{'input_tokens':4}}]}}
             for condition,cid in schedule()]
        report=check_inputs(FakeTokenizer(),old)
        self.assertTrue(report['passed'])
        old[0]['judgement']['attempts'][0]['generation']['input_tokens']=999
        self.assertFalse(check_inputs(FakeTokenizer(),old)['passed'])

    def test_controlled_reference_and_reject_fake_preflight(self):
        report=verify_reference()
        self.assertTrue(report['rubric_unchanged'])
        self.assertTrue(report['acceptance_unchanged'])
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'proof.json'
            path.write_text(json.dumps({'passed':False}),encoding='utf-8')
            with self.assertRaises(ValueError):verify_preflight(path)

    def test_legacy_constructor_and_method_not_silently_replaced(self):
        from response_v4 import TrackedGenerator
        self.assertIs(CausalGenerator.generate,TrackedGenerator.generate)
        self.assertIsNot(NativeChatGenerator.generate,CausalGenerator.generate)
