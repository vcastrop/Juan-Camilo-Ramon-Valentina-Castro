"""Transcription-only parsing: no corpus, gold or hidden field completion."""
import re
from final.integration import normalized

FIELDS = {
    'identificador del contrato': 'id_contrato', 'id del contrato': 'id_contrato',
    'id contrato': 'id_contrato', 'id_contrato': 'id_contrato',
    'objeto registrado': 'objeto', 'objeto del contrato': 'objeto', 'objeto': 'objeto',
    'modalidad de contratacion': 'modalidad', 'modalidad': 'modalidad',
    'valor del contrato (cop)': 'valor_cop', 'valor del contrato': 'valor_cop',
    'valor (cop)': 'valor_cop', 'valor_cop': 'valor_cop',
}


def amount_literal(value):
    s = re.sub(r'(?i)\bCOP\b|\$', '', value).strip()
    if re.fullmatch(r'\d+', s):
        return s
    if re.fullmatch(r'\d{1,3}(?:\.\d{3})+(?:,\d{2})?', s):
        return s.replace('.', '').replace(',', '.')
    if re.fullmatch(r'\d{1,3}(?:,\d{3})+(?:\.\d{2})?', s):
        return s.replace(',', '')
    if re.fullmatch(r'\d+[.,]\d{2}', s):
        return s.replace(',', '.')
    return None


def transcription_to_visual(raw):
    from structured_output import parse_object
    data = parse_object(raw)
    if set(data) != {'legible', 'texto_visible'} or type(data['legible']) is not bool:
        raise ValueError('Expected exactly legible and texto_visible')
    text = data['texto_visible']
    if text is not None and (not isinstance(text, str) or len(text) > 8000):
        raise ValueError('Invalid transcription')
    output = {'legible': data['legible'], 'texto_visible': text,
              'id_contrato': None, 'objeto': None, 'modalidad': None, 'valor_cop': None}
    if not data['legible']:
        if text and text.strip():
            raise ValueError('Unreadable image with asserted text')
        output['texto_visible'] = None
        return output, {}
    if not text or not text.strip():
        raise ValueError('Readable image without text')
    collected, current = {}, None
    for line in text.splitlines():
        match = re.match(r'^\s*([^:\n]{1,75}):\s*(.*)$', line)
        if match:
            current = FIELDS.get(normalized(match.group(1)))
            if current:
                collected.setdefault(current, []).append(match.group(2).strip())
        elif current and line.strip():
            collected[current][-1] += ' '+line.strip()
    evidence = {}
    for key, literals in collected.items():
        unique = {s.strip() for s in literals if s.strip()}
        evidence[key] = {'observed_literals': sorted(unique), 'ambiguous': len(unique) != 1}
        if len(unique) != 1:
            continue
        literal = next(iter(unique))
        if key == 'id_contrato':
            output[key] = literal if re.fullmatch(r'CO1\.PCCNTR\.\d+', literal) else None
        elif key == 'valor_cop':
            output[key] = amount_literal(literal)
        else:
            output[key] = literal
    if not any(output[k] is not None for k in ('id_contrato', 'objeto', 'modalidad', 'valor_cop')):
        raise ValueError('No recognized contractual fields in transcription')
    return output, evidence


def uniform_image(image):
    """Conservative pixel guard, not a general legibility or OCR classifier."""
    low, high = image.convert('L').getextrema()
    return high-low <= 2


def requested_missing(question, visual):
    q = normalized(question)
    required = set()
    if re.search(r'\bmodalidad\b', q):
        required.add('modalidad')
    if re.search(r'\b(valor|monto|importe)\b', q):
        required.add('valor_cop')
    if re.search(r'\bobjeto\b', q):
        required.add('objeto')
    return sorted(k for k in required if visual.get(k) is None)
