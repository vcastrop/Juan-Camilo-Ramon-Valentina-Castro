"""ZeroGPU-only initialization; inherited M1 inference and checkpoint unchanged."""
import json
from pathlib import Path
import tempfile
import zipfile

from final.adapters import Classifier,ROOT,MODELS


class CPUClassifier(Classifier):
    def __init__(self):
        import torch
        from transformers import AutoTokenizer,AutoModelForSequenceClassification
        from peft import PeftModel
        self.torch=torch
        self.temp=tempfile.TemporaryDirectory(prefix='contractrisk_final_m1_')
        folder=Path(self.temp.name)
        with zipfile.ZipFile(ROOT/'model/contractrisk_robertalex_lora_adapter.zip') as z:
            for member in z.infolist():
                if not (folder/member.filename).resolve().is_relative_to(folder.resolve()):
                    raise ValueError('Unsafe adapter archive')
            z.extractall(folder)
        configs=list(folder.rglob('adapter_config.json'))
        if len(configs)!=1:raise ValueError('Ambiguous adapter')
        path=configs[0].parent
        config=json.loads(configs[0].read_text())
        if config['base_model_name_or_path']!=MODELS['classifier'][0]:raise ValueError('Unexpected base model')
        self.tokenizer=AutoTokenizer.from_pretrained(path)
        base=AutoModelForSequenceClassification.from_pretrained(
            MODELS['classifier'][0],revision=MODELS['classifier'][1],num_labels=2,
            id2label={0:'REQUIERE_REVISION',1:'SUFICIENTE'},
            label2id={'REQUIERE_REVISION':0,'SUFICIENTE':1})
        self.model=PeftModel.from_pretrained(base,path,torch_device='cpu').to('cpu').eval()
