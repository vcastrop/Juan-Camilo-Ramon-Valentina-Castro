"""OCR deployment boundary, separate from the historical VLM health contract."""
from final.service_contract import Service, event

EVALUATED_LANGUAGES={
    'spa':'6f2e04d02774a18f01bed44b1111f2cd7f3ba7ac9dc4373cd3f898a40ea6b464',
    'eng':'7d4322bd2a7749724879683fc3912cb542f19906c83bcc1a52132556427170b2'}


class OCRService(Service):
    def health(self):
        data=super().health()
        try: reader=self.backend.reader_state() if self.backend else {}
        except Exception:reader={}
        if not isinstance(reader,dict):reader={}
        required={'generator','classifier','embedding','reranker'}
        models=data['models_loaded']
        reader_ready=(reader.get('ready') is True and reader.get('kind')=='tesseract_cpu_not_qwen_vlm'
                      and str(reader.get('version','')).startswith('tesseract 5.')
                      and set(reader.get('language_data_sha256',{}))=={'spa','eng'})
        data.update(contract_system_ready=(set(models)==required and all(v is True for v in models.values())
                    and reader_ready and data['index_ready'] and self.boot_error is None),
                    deployment_profile='integrated_ocr20_fp16',neural_models_expected=4,vlm_loaded=False,
                    visual_reader=reader,visual_reader_ready=reader_ready,
                    evaluated_language_data_match=reader.get('language_data_sha256')==EVALUATED_LANGUAGES,
                    reference_evaluation_environment='Colab T4; Tesseract 5.3.4; public environment requires separate smoke verification')
        return data

    def compute(self,question,mode,description,image,consent):
        if not self.health()['contract_system_ready']:
            return {'error':'not_ready','message':'Los cuatro modelos, OCR o índice no están listos.'},event(self.version,0,mode,error='not_ready')
        return super().compute(question,mode,description,image,consent)
