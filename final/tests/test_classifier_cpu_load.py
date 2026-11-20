import sys
import types
import unittest
from unittest.mock import Mock,patch


class ClassifierCPULoadTests(unittest.TestCase):
    def test_trained_adapter_weights_loaded_on_cpu_before_model_to_cpu(self):
        from final.adapters import Classifier
        from final.config import MODELS
        model=Mock();model.to.return_value=model;model.eval.return_value=model
        base=object()
        loader=Mock()
        def load(base_model,path,**kwargs):
            # Reproduce the unsafe automatic-device path without Torch/GPU/network.
            if kwargs.get('torch_device')!='cpu':raise RuntimeError('simulated ZeroGPU automatic CUDA load')
            self.assertIs(base_model,base)
            self.assertTrue((path/'adapter_model.safetensors').is_file())
            self.assertTrue((path/'adapter_config.json').is_file())
            return model
        loader.from_pretrained.side_effect=load
        base_loader=Mock();base_loader.from_pretrained.return_value=base
        tokenizer=Mock();tokenizer.from_pretrained.return_value='existing_tokenizer'
        modules={'torch':types.SimpleNamespace(),
                 'transformers':types.SimpleNamespace(AutoTokenizer=tokenizer,AutoModelForSequenceClassification=base_loader),
                 'peft':types.SimpleNamespace(PeftModel=loader)}
        with patch.dict(sys.modules,modules):classifier=Classifier()
        try:
            self.assertIs(classifier.model,model)
            loader.from_pretrained.assert_called_once()
            model.to.assert_called_once_with('cpu')
            model.eval.assert_called_once()
            self.assertEqual(base_loader.from_pretrained.call_args.kwargs['revision'],MODELS['classifier'][1])
            self.assertEqual(base_loader.from_pretrained.call_args.kwargs['num_labels'],2)
        finally:classifier.temp.cleanup()
