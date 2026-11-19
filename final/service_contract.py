"""Bounded public request boundary. Logs carry metadata only, not query/image/OCR data."""
from datetime import datetime, timezone
import math
import re
import time
import uuid

from final.tool_usage import metrics

EVENT_KEYS = {'timestamp_utc', 'request_id', 'event_type', 'latency_seconds', 'success', 'mode',
              'rag_used', 'tool_used', 'vision_used', 'classifier_used', 'router_used', 'abstention',
              'components_known', 'error_code', 'phase', 'version'}
ERRORS = {'none', 'invalid_input', 'not_ready', 'busy', 'runtime_error', 'gpu_dispatch_error'}


def validate_event(payload):
    if not isinstance(payload, dict) or set(payload) != EVENT_KEYS:
        raise ValueError('Unexpected event fields')
    if not re.fullmatch(r'[a-f0-9]{40}', str(payload['version'])):
        raise ValueError('Version must be a full source commit')
    if payload['event_type'] != 'contract_request' or payload['phase'] != 'contractual_candidate':
        raise ValueError('Unexpected event kind')
    if payload['mode'] not in {'qa', 'sufficiency', 'unknown'} or payload['error_code'] not in ERRORS:
        raise ValueError('Unexpected event category')
    if str(uuid.UUID(payload['request_id'])) != payload['request_id']:
        raise ValueError('Unexpected request ID')
    timestamp = datetime.fromisoformat(payload['timestamp_utc'])
    if timestamp.utcoffset() != timezone.utc.utcoffset(timestamp):
        raise ValueError('UTC timestamp required')
    seconds = payload['latency_seconds']
    if type(seconds) not in {int, float} or not math.isfinite(seconds) or not 0 <= seconds < 3600:
        raise ValueError('Invalid event latency')
    for name in ['success', 'components_known']:
        if type(payload[name]) is not bool: raise ValueError('Boolean required')
    for name in ['rag_used', 'tool_used', 'vision_used', 'classifier_used', 'router_used', 'abstention']:
        if payload[name] is not None and type(payload[name]) is not bool:
            raise ValueError('Boolean or unknown required')
    return payload


class InputError(ValueError):
    pass


def validate(question, mode, description, image, consent):
    if consent is not True: raise InputError('Confirma el aviso de uso y privacidad antes de consultar.')
    if not isinstance(mode, str) or mode not in {'qa', 'sufficiency'}: raise InputError('Modo no permitido.')
    if not isinstance(description, str) or len(description) > 8000:
        raise InputError('La descripción debe tener como máximo 8000 caracteres.')
    if not isinstance(question, str) or len(question) > 1200:
        raise InputError('La pregunta debe tener como máximo 1200 caracteres.')
    question = question.strip()
    if mode == 'qa' and not question: raise InputError('Escribe una pregunta para consultar las fuentes.')
    if mode == 'sufficiency':
        question = question or 'Evaluar suficiencia descriptiva del texto contractual.'
        if not description.strip() and image is None:
            raise InputError('Introduce una descripción o una imagen con objeto legible.')
    if image is not None:
        from PIL import Image
        if not isinstance(image, Image.Image): raise InputError('Se requiere una imagen válida.')
        if min(image.size) <= 0 or image.width*image.height > 12_000_000:
            raise InputError('La imagen supera el límite de 12 millones de píxeles.')
    return question


def event(version, seconds, mode='qa', record=None, error='none'):
    if error not in ERRORS: raise ValueError('Unknown technical error code')
    seconds = float(seconds)
    if not math.isfinite(seconds) or not 0 <= seconds < 3600: raise ValueError('Invalid latency')
    known = isinstance(record, dict)
    c = record.get('components', {}) if known else {}
    use = metrics(record) if known else None
    return {'timestamp_utc': datetime.now(timezone.utc).isoformat(), 'request_id': str(uuid.uuid4()),
            'event_type': 'contract_request', 'latency_seconds': seconds, 'success': known and error == 'none',
            'mode': mode if isinstance(mode, str) and mode in {'qa', 'sufficiency'} else 'unknown',
            'rag_used': bool(c.get('rag')) if known else None,
            'tool_used': use['tool_success'] if known else None,
            'vision_used': bool(c.get('vision')) if known else None,
            'classifier_used': bool(c.get('classifier')) if known else None,
            'router_used': use['router_used'] if known else None,
            'abstention': (record.get('output') or {}).get('abstencion') if known else None,
            'components_known': known, 'error_code': error, 'phase': 'contractual_candidate', 'version': version}


class Service:
    def __init__(self, backend, version, boot_error=None):
        self.backend, self.version, self.boot_error = backend, version, boot_error
        self.last_real_request_verified = False

    def health(self):
        try: models = self.backend.model_state() if self.backend else {}
        except Exception: models = {}
        if not isinstance(models, dict): models = {}
        try: index = bool(self.backend and self.backend.index_probe())
        except Exception: index = False
        required = {'generator', 'vision', 'classifier', 'embedding', 'reranker'}
        ready = set(models) == required and all(v is True for v in models.values()) and index and self.boot_error is None
        return {'status': 'alive', 'phase': 'contractual_candidate', 'contract_system_ready': ready,
                'models_loaded': models, 'index_ready': index, 'version': self.version,
                'real_request_verified': self.last_real_request_verified,
                'gpu_allocation': 'on_demand_not_reserved_by_health_check',
                'startup_error': self.boot_error}

    def compute(self, question, mode, description, image, consent):
        started = time.perf_counter()
        try:
            question = validate(question, mode, description, image, consent)
        except InputError:
            return {'error': 'invalid_input', 'message': 'Revisa los límites y el consentimiento de entrada.'}, event(self.version, time.perf_counter()-started, mode, error='invalid_input')
        if self.backend is None or self.boot_error is not None:
            return {'error': 'not_ready', 'message': 'Los componentes reales no están listos; no se simula una respuesta.'}, event(self.version, time.perf_counter()-started, mode, error='not_ready')
        try:
            record = self.backend.predict(question, image=image, mode=mode,
                                          description=description.strip() or None)
            output = record['output']
            if not isinstance(output, dict): raise ValueError('Missing structured output')
            # Return only what the visitor needs; raw model traces/OCR stay out of UI/logs.
            display = {'resultado': output, 'fuentes': [{'fragmento': c['chunk_id'], 'texto': c['text'],
                       'url': c.get('source_url')} for c in record.get('contexts', [])],
                       'clasificacion': record.get('classification'), 'control_activado': record.get('guard'),
                       'advertencia': 'Sistema académico experimental. Verifica las fuentes; no determina fraude ni autenticidad. La decisión corresponde a una persona.'}
            return display, event(self.version, time.perf_counter()-started, mode, record)
        except Exception:
            return {'error': 'runtime_error', 'message': 'No se pudo completar la consulta. No se sustituye por una respuesta inventada.'}, event(self.version, time.perf_counter()-started, mode, error='runtime_error')

    def observe_finished(self, payload):
        # Run in CPU callback AFTER the ZeroGPU result, not only in a worker process.
        if payload.get('success') is True: self.last_real_request_verified = True
