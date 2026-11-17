"""Pure orchestration with injected real adapters. No gold data enters inference."""
import json
import re
import time
import unicodedata
from final.config import VERSION


def normalized(text):
    return ' '.join(''.join(c for c in unicodedata.normalize('NFD', text.casefold())
                           if not unicodedata.combining(c)).split())


def contract_ids(text):
    return set(re.findall(r'CO1\.PCCNTR\.\d+\b', text.upper()))


def abstain(reason):
    return {'respuesta': 'No dispongo de evidencia suficiente para responder.',
            'explicacion': reason, 'citas': [], 'abstencion': True}


def parse_visual(raw):
    from structured_output import parse_object
    data = parse_object(raw)
    keys = {'legible', 'texto_visible', 'id_contrato', 'objeto', 'modalidad', 'valor_cop'}
    if set(data) != keys or type(data['legible']) is not bool:
        raise ValueError('Visual schema mismatch')
    for key in keys - {'legible'}:
        if data[key] is not None and (not isinstance(data[key], str) or len(data[key]) > 8000):
            raise ValueError('Visual fields must be strings or null')
    if data['legible'] and not (data['texto_visible'] or '').strip():
        raise ValueError('Readable image without transcription')
    if not data['legible'] and any(data[k] for k in keys - {'legible'}):
        raise ValueError('Unreadable image with asserted fields')
    if data['id_contrato'] and not re.fullmatch(r'CO1\.PCCNTR\.\d+', data['id_contrato']):
        raise ValueError('Invalid visual ID')
    if data['id_contrato'] and data['id_contrato'] not in contract_ids(data['texto_visible'] or ''):
        raise ValueError('Visual ID missing from transcription')
    if data['valor_cop'] and not re.fullmatch(r'\d+(?:\.\d+)?', data['valor_cop']):
        raise ValueError('Ambiguous visual amount; use decimal string or null')
    return data


class IntegratedSystem:
    def __init__(self, documents, answer, classifier=None, vision=None):
        self.documents = {d['doc_id']: d for d in documents}
        self.answer, self.classifier, self.vision = answer, classifier, vision

    def predict(self, question, image=None, mode='qa', description=None):
        start = time.perf_counter()
        if not isinstance(question, str) or not 0 < len(question.strip()) <= 1200:
            raise ValueError('Question must contain 1-1200 characters')
        if mode not in {'qa', 'sufficiency'}:
            raise ValueError('Unsupported mode')
        record = {'question': question, 'mode': mode, 'visual': None,
                  'classification': None, 'contexts': [], 'tool_trace': [],
                  'components': {'rag': False, 'tool': False, 'vision': False, 'classifier': False},
                  'integration_version': VERSION}
        def finish(output, guard=None):
            record.update(output=output, guard=guard, latency_seconds=time.perf_counter()-start)
            return record
        visual = None
        visual_context = None
        if image is not None:
            if self.vision is None:
                raise RuntimeError('Vision component not loaded')
            record['components']['vision'] = True
            result = self.vision.extract(image)
            record['visual'] = result
            if result.get('parse_error'):
                return finish(abstain('No se pudo validar la lectura de la imagen.'), 'visual_schema')
            visual = result['output']
            if not visual['legible']:
                return finish(abstain('La imagen no es legible. Se necesita una captura más clara.'), 'unreadable')
            if contract_ids(question) and visual['id_contrato'] and visual['id_contrato'] not in contract_ids(question):
                return finish(abstain('El ID de la pregunta y el leído en la imagen no coinciden.'), 'id_mismatch')
            from final.visual_fields import requested_missing
            missing = requested_missing(question, visual)
            if mode == 'qa' and missing:
                record['missing_visual_fields'] = missing
                return finish(abstain('La lectura de la imagen no permite verificar todos los campos solicitados.'), 'missing_visual_fields')
            visual_context = {'doc_id': visual['id_contrato'] or 'IMAGE', 'chunk_id': 'IMAGE::input',
                              'text': json.dumps(visual, ensure_ascii=False), 'source_url': 'uploaded-image',
                              'evidence_type': 'unverified_visual_extraction'}
            record['visual_evidence_warning'] = 'Lectura del modelo, no verificación del documento ni autenticidad.'
            if mode == 'qa':
                from final.source_consistency import compare_visual_source, conflict_explanation
                document = self.documents.get(visual['id_contrato'])
                consistency = compare_visual_source(visual, document)
                record['source_consistency'] = consistency
                if consistency['status'] == 'conflict':
                    source_context = {'doc_id': document['doc_id'], 'chunk_id': document['doc_id']+'::full_record',
                                      'text': document['text'], 'source_url': document['source_url'],
                                      'evidence_type': 'complete_source_record'}
                    record['contexts'] = [visual_context,source_context]
                    output = abstain(conflict_explanation(consistency))
                    output['citas'] = [visual_context['chunk_id'], source_context['chunk_id']]
                    return finish(output, 'visual_source_conflict')
        if mode == 'sufficiency':
            text = description if description is not None else (visual or {}).get('objeto')
            if not isinstance(text, str) or not text.strip():
                return finish(abstain('Se necesita una descripción contractual legible.'), 'missing_description')
            if len(text) > 8000:
                raise ValueError('Description too long')
            if self.classifier is None:
                raise RuntimeError('Classifier not loaded')
            record['components']['classifier'] = True
            label = self.classifier.classify(text)
            record['classification'] = label
            return finish({'respuesta': label['label'],
                           'explicacion': 'Señal de suficiencia textual; no determina fraude. Requiere revisión humana.',
                           'citas': [], 'abstencion': False})
        q = normalized(question)
        if re.search(r'\b(auditoria|clausula|clausulado|informe de ejecucion|ejecucion fisica)\b', q):
            return finish(abstain('El corpus contiene fichas de registro, no cláusulas ni informes de auditoría.'), 'absent_source_type')
        wanted = contract_ids(question)
        if image is None and wanted - set(self.documents):
            return finish(abstain('El contrato solicitado no pertenece al snapshot disponible.'), 'unknown_contract')
        # Only user inputs/source evidence, never expected answers or judge scores.
        result = self.answer(question, visual_context)
        record.update({k: v for k, v in result.items() if k not in {'question', 'latency_seconds'}})
        record['components']['rag'] = True
        record['components']['tool'] = bool(result.get('tool_calls', 0))
        output = result.get('output')
        if output is None:
            return finish(abstain('El modelo no produjo una respuesta estructurada válida.'), 'answer_schema')
        return finish(output)
