"""Final M3 harness: same eval set and rules for every row. Version frozen before the gold run.

Rules are fixed here, not tuned on gold results. Gold fields are used only AFTER each
system answered, to score; the system receives exclusively the question text.
"""
import re
import statistics
import time
import unicodedata

HARNESS_VERSION = 'm3-harness-1.0'
CONTRACT_ID = re.compile(r'CO1\.PCCNTR\.\d+', re.IGNORECASE)
FACT_TOKEN_COVERAGE = 0.8
ISO_DATE = re.compile(r'\d{4}-\d{2}-\d{2}')
# Asserting fraud etc. is a domain failure; a negated mention ("no permite concluir fraude") is not.
ACCUSATION = re.compile(r'\b(fraude|corrupci[oó]n|sobrecosto|peculado|detrimento patrimonial|'
                        r'irregularidad(?:es)? (?:confirmada|demostrada|comprobada))', re.IGNORECASE)
NEGATION = re.compile(r'\b(no|sin|ni|tampoco|ning[uú]n[ao]?)\b', re.IGNORECASE)
RULES = {
    'dimension_1': 'Exactitud verificable 0-1. Respondible: fracción de required_facts (o fechas ISO del esperado si la lista está vacía) presentes en respuesta+explicacion normalizadas (coincidencia exacta o >=80% de sus palabras de 3+ letras; cifras siempre exactas); abstenerse vale 0 salvo en inconsistency. No respondible: 1 si abstencion=true. Salida inválida: 0.',
    'dimension_2': 'Juez m3-judge-1.0 sin mitigación de verbosidad (la mitigación empeoró la medida en v5). Promedio solo de notas válidas, con cobertura; nunca se imputa ni reemplaza una nota.',
    'dimension_3': 'Cumplimiento de dominio (pasa/no pasa). Respondible: exactitud=1, cita todas las fichas requeridas, no cita fichas ajenas y no acusa. No respondible: abstencion=true, sin cifras afirmadas y sin acusación. Salida inválida: no pasa.',
    'm2_compatible': 'Regla de dominio de M2 trasladada: exactitud=1 y juez>=4 (sin juez válido no pasa).',
    'similarity': 'Similitud coseno respuesta/esperado con el embedding del índice (métrica de S07); solo diagnóstico, sensible a paráfrasis.',
    'latency': 'Mediana de latency_seconds de predict(): pregunta a respuesta final, con recuperación, reranking y herramienta; excluye carga, índice y juez.',
}


def normalize(text):
    text = ''.join(c for c in unicodedata.normalize('NFD', str(text).casefold())
                   if unicodedata.category(c) != 'Mn')
    text = re.sub(r'(?<=\d)[.,\s](?=\d{3}(?!\d))', '', text)  # 250.000.000 -> 250000000
    return ' '.join(re.sub(r'[^0-9a-z]+', ' ', text).split())


def fact_present(fact, text):
    """Exact normalized match, or >= FACT_TOKEN_COVERAGE of the fact's words (paraphrase tolerance)."""
    fact_n, text_n = normalize(fact), normalize(text)
    if fact_n in text_n:
        return True
    words = {w for w in fact_n.split() if len(w) >= 3}
    if not words or any(w.isdigit() for w in words):
        return False  # numbers must match exactly
    return len(words & set(text_n.split()))/len(words) >= FACT_TOKEN_COVERAGE


def answer_text(output):
    return f"{output.get('respuesta', '')} {output.get('explicacion', '')}"


def required_facts(case):
    facts = case.get('required_facts') or []
    if not facts and case.get('kind') == 'inconsistency':
        facts = sorted(set(ISO_DATE.findall(case['expected'])))
    return facts


def cited_docs(output):
    return {c.split('::', 1)[0].upper() for c in output.get('citas', [])}


def asserts_accusation(text):
    for match in ACCUSATION.finditer(text):
        if not NEGATION.search(text[max(0, match.start()-40):match.start()]):
            return True
    return False


def asserts_amount(text):
    return bool(re.search(r'\d{4,}', normalize(CONTRACT_ID.sub(' ', text))))


def score_case(case, record):
    """Deterministic dimensions 1 and 3 for one record; gold is read only here."""
    output = record.get('output')
    answerable = case['kind'] != 'unanswerable'
    row = {'eval_id': case['eval_id'], 'kind': case['kind'], 'answerable': answerable,
           'valid_output': isinstance(output, dict)}
    if not row['valid_output']:
        row.update(accuracy=0.0, facts_found=[], facts_missing=required_facts(case), domain_pass=False,
                   domain_reasons=['salida_invalida'])
        return row
    text = answer_text(output)
    reasons = []
    if asserts_accusation(text):
        reasons.append('acusacion')
    if answerable:
        facts = required_facts(case)
        found = [f for f in facts if fact_present(f, text)]
        abstained = output['abstencion'] and case['kind'] != 'inconsistency'
        accuracy = 0.0 if abstained or not facts else len(found)/len(facts)
        docs, wanted = cited_docs(output), {s.upper() for s in case['source_ids']}
        if abstained:
            reasons.append('abstencion_indebida')
        if accuracy < 1:
            reasons.append('hechos_incompletos')
        if not wanted.issubset(docs):
            reasons.append('falta_cita_requerida')
        if docs - wanted:
            reasons.append('cita_ficha_ajena')
        row.update(accuracy=accuracy, facts_found=found, facts_missing=[f for f in facts if f not in found])
    else:
        row.update(accuracy=1.0 if output['abstencion'] else 0.0, facts_found=[], facts_missing=[])
        if not output['abstencion']:
            reasons.append('no_se_abstiene')
        if asserts_amount(output.get('respuesta', '')):
            reasons.append('afirma_cifras')
    row.update(domain_pass=not reasons, domain_reasons=reasons)
    return row


def cosine(a, b):
    import numpy as np
    return float(np.dot(a, b)/(np.linalg.norm(a)*np.linalg.norm(b)))


def similarity(encoder, output, expected):
    if encoder is None or not isinstance(output, dict):
        return None
    vectors = encoder.encode([output['respuesta'], expected])
    return cosine(vectors[0], vectors[1])


def harness(eval_set, sistema, juez=None, encoder=None, emit=None, nombre=''):
    """Run `sistema(pregunta) -> record` over every case and score it with the frozen rules."""
    rows = []
    for i, case in enumerate(eval_set):
        print(f'{nombre}: {i+1}/{len(eval_set)} {case["eval_id"]}', flush=True)
        try:
            record = sistema(case['input'])  # only the question reaches the system
            error = None
        except Exception as exc:  # recorded as a failed case, never silently dropped
            record, error = {'question': case['input'], 'output': None, 'contexts': [],
                             'latency_seconds': None}, f'{type(exc).__name__}: {exc}'
        row = score_case(case, record)
        row.update(variant=nombre, system_error=error, latency_seconds=record.get('latency_seconds'),
                   similarity=similarity(encoder, record.get('output'), case['expected']))
        if juez is not None:
            start = time.perf_counter()
            judgement = juez.evaluate(record)
            judgement['wall_seconds'] = time.perf_counter()-start
        else:
            judgement = None
        row['judge_score'] = judgement['score'] if judgement else None
        row['m2_compatible_pass'] = bool(row['accuracy'] == 1 and row['judge_score'] is not None
                                         and row['judge_score'] >= 4)
        full = {'row': row, 'record': record, 'judgement': judgement}
        rows.append(full)
        if emit:
            emit(full)
    return rows, scorecard([r['row'] for r in rows])


def _mean(values):
    values = [v for v in values if v is not None]
    return statistics.mean(values) if values else None


def scorecard(rows):
    """Aggregate over ALL cases; missing judge notes and latencies are counted, not imputed."""
    total = len(rows)
    latencies = [r['latency_seconds'] for r in rows if r.get('latency_seconds') is not None]
    judged = [r['judge_score'] for r in rows if r.get('judge_score') is not None]
    answerable = [r for r in rows if r['answerable']]
    unanswerable = [r for r in rows if not r['answerable']]
    return {'harness_version': HARNESS_VERSION, 'cases': total,
            'valid_outputs': sum(r['valid_output'] for r in rows),
            'dim1_accuracy': _mean([r['accuracy'] for r in rows]),
            'dim2_judge_mean': _mean(judged), 'dim2_judge_valid': len(judged),
            'dim3_domain_rate': sum(r['domain_pass'] for r in rows)/total if total else None,
            'dim3_domain_passed': sum(r['domain_pass'] for r in rows),
            'm2_compatible_rate': sum(r['m2_compatible_pass'] for r in rows)/total if total else None,
            'similarity_mean': _mean([r.get('similarity') for r in rows]),
            'answerable_accuracy': _mean([r['accuracy'] for r in answerable]),
            'unanswerable_abstained': sum(r['accuracy'] == 1 for r in unanswerable),
            'unanswerable_total': len(unanswerable),
            'latency_median_seconds': statistics.median(latencies) if latencies else None,
            'latency_cases': len(latencies),
            'system_errors': sum(bool(r.get('system_error')) for r in rows)}
