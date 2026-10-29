"""Harness m3-harness-1.1: corrects deterministic defects of 1.0 found in post-run review.

1.0 stays unchanged because it produced the original final run. 1.1 only re-scores the
SAVED responses (no regeneration, no answer selection) and reuses the saved raw judge notes.
Changes, all motivated by documented false positives, none by a target number:
- number facts need digit boundaries ('168000000' is not present in '1680000000');
- an exact fact preceded by a negation in the same phrase ('no es mínima cuantía') is absent;
- any mention of irregularity/fraud etc. counts as an accusation unless negated in its own
  clause ('sugiere una posible irregularidad' fails; 'ni permite concluir una irregularidad' passes);
- adds a retrieval diagnostic: required facts present in the context given to the generator.
"""
import re
import statistics
from harness_m3 import (FACT_TOKEN_COVERAGE, answer_text, asserts_amount, cited_docs, normalize,
                        required_facts)

HARNESS_VERSION = 'm3-harness-1.1'
NEGATIONS = {'no', 'ni', 'sin', 'tampoco', 'nunca'}
ACCUSATION = re.compile(r'\b(irregularidad(?:es)?|irregular(?:es)?|fraude|fraudulent[oa]s?|corrupci[oó]n|'
                        r'sobrecostos?|peculado|detrimento patrimonial|ilegal(?:es|idad)?)\b', re.IGNORECASE)
NEGATION = re.compile(r'\b(no|ni|sin|tampoco|nunca)\b', re.IGNORECASE)
RULES = {
    'dimension_1': 'Cobertura automática de hechos requeridos 0-1 (no es accuracy por respuesta): fracción de required_facts (fechas ISO del esperado en inconsistency) encontrados en respuesta+explicacion normalizadas. Coincidencia exacta con límites de número y sin negación en las 3 palabras previas, o >=80% de las palabras de 3+ letras del hecho (paráfrasis; sin control de negación). Abstenerse vale 0 salvo en inconsistency. No respondible: 1 si abstencion=true. Salida inválida: 0. Se informa aparte el número de respuestas con cobertura completa.',
    'dimension_2': 'Igual que 1.0: notas brutas del juez m3-judge-1.0 guardadas en la corrida; no se vuelve a juzgar.',
    'dimension_3': 'Chequeo automático de dominio (no certifica aptitud): respondible = cobertura completa, cita todas las fichas requeridas, no cita fichas ajenas y no menciona irregularidad/fraude/sobrecosto salvo negado en la misma cláusula. No respondible = abstencion=true, sin cifras afirmadas y sin esa mención.',
    'evidence_in_context': 'Diagnóstico de recuperación: fracción de hechos requeridos presentes en los fragmentos recuperados (sin tool_value) y en todo lo entregado al generador (fragmentos, campos tool_value y operación calculada por la herramienta).',
}


def fact_present(fact, text):
    fact_n, text_n = normalize(fact), normalize(text)
    matches = list(re.finditer(r'(?<![0-9a-z])' + re.escape(fact_n) + r'(?![0-9])', text_n))
    if matches:
        # Present only if some occurrence is not negated; a negated exact mention is not a paraphrase.
        return any(not NEGATIONS.intersection(text_n[:m.start()].split()[-3:]) for m in matches)
    words = {w for w in fact_n.split() if len(w) >= 3}
    if not words or any(w.isdigit() for w in words):
        return False
    return len(words & set(text_n.split()))/len(words) >= FACT_TOKEN_COVERAGE


def asserts_accusation(text):
    for match in ACCUSATION.finditer(text):
        clause = re.split(r'[.;,:\n]', text[:match.start()])[-1]
        if not NEGATION.search(clause):
            return True
    return False


def evidence_coverage(facts, contexts, tool_lines=()):
    if not facts:
        return None
    text = '\n'.join([c['text'] for c in contexts] + list(tool_lines))
    return sum(fact_present(f, text) for f in facts)/len(facts)


def tool_operations(record):
    return [e['tool_result']['operation'] for e in record.get('tool_trace', [])
            if e.get('tool_result') and e['tool_result'].get('ok')]


def score_case(case, record):
    output = record.get('output')
    answerable = case['kind'] != 'unanswerable'
    facts = required_facts(case) if answerable else []
    contexts = record.get('contexts', [])
    retrieved = [c for c in contexts if not c['chunk_id'].endswith('::tool_value')]
    row = {'eval_id': case['eval_id'], 'kind': case['kind'], 'answerable': answerable,
           'valid_output': isinstance(output, dict),
           'evidence_retrieved': evidence_coverage(facts, retrieved),
           'evidence_with_tool': evidence_coverage(facts, contexts, tool_operations(record))}
    if not row['valid_output']:
        row.update(coverage=0.0, facts_found=[], facts_missing=facts, domain_pass=False,
                   domain_reasons=['salida_invalida'])
        return row
    text = answer_text(output)
    reasons = ['menciona_irregularidad'] if asserts_accusation(text) else []
    if answerable:
        found = [f for f in facts if fact_present(f, text)]
        abstained = output['abstencion'] and case['kind'] != 'inconsistency'
        coverage = 0.0 if abstained or not facts else len(found)/len(facts)
        docs, wanted = cited_docs(output), {s.upper() for s in case['source_ids']}
        if abstained:
            reasons.append('abstencion_indebida')
        if coverage < 1:
            reasons.append('hechos_incompletos')
        if not wanted.issubset(docs):
            reasons.append('falta_cita_requerida')
        if docs - wanted:
            reasons.append('cita_ficha_ajena')
        row.update(coverage=coverage, facts_found=found, facts_missing=[f for f in facts if f not in found])
    else:
        row.update(coverage=1.0 if output['abstencion'] else 0.0, facts_found=[], facts_missing=[])
        if not output['abstencion']:
            reasons.append('no_se_abstiene')
        if asserts_amount(output.get('respuesta', '')):
            reasons.append('afirma_cifras')
    row.update(domain_pass=not reasons, domain_reasons=reasons)
    return row


def rescore(case, item):
    """Re-score one saved harness item; the judge note is copied, never regenerated or changed."""
    old = item['row']
    row = score_case(case, item['record'])
    row.update(variant=old['variant'], system_error=old.get('system_error'),
               latency_seconds=old.get('latency_seconds'), judge_score=old.get('judge_score'),
               v10_accuracy=old['accuracy'], v10_domain_pass=old['domain_pass'])
    row['m2_compatible_pass'] = bool(row['coverage'] == 1 and row['judge_score'] is not None
                                     and row['judge_score'] >= 4)
    return row


def _mean(values):
    values = [v for v in values if v is not None]
    return statistics.mean(values) if values else None


def scorecard(rows):
    total = len(rows)
    latencies = [r['latency_seconds'] for r in rows if r.get('latency_seconds') is not None]
    judged = [r['judge_score'] for r in rows if r.get('judge_score') is not None]
    answerable = [r for r in rows if r['answerable']]
    unanswerable = [r for r in rows if not r['answerable']]
    return {'harness_version': HARNESS_VERSION, 'cases': total,
            'valid_outputs': sum(r['valid_output'] for r in rows),
            'dim1_fact_coverage': _mean([r['coverage'] for r in rows]),
            'dim1_complete_answers': sum(r['coverage'] == 1 for r in rows),
            'dim2_judge_mean': _mean(judged), 'dim2_judge_valid': len(judged),
            'dim3_domain_passed': sum(r['domain_pass'] for r in rows),
            'dim3_domain_rate': sum(r['domain_pass'] for r in rows)/total if total else None,
            'm2_compatible_rate': sum(r['m2_compatible_pass'] for r in rows)/total if total else None,
            'answerable_fact_coverage': _mean([r['coverage'] for r in answerable]),
            'unanswerable_abstained': sum(r['coverage'] == 1 for r in unanswerable),
            'unanswerable_total': len(unanswerable),
            'evidence_retrieved_mean': _mean([r['evidence_retrieved'] for r in answerable]),
            'evidence_retrieved_complete': sum(r['evidence_retrieved'] == 1 for r in answerable),
            'evidence_with_tool_complete': sum(r['evidence_with_tool'] == 1 for r in answerable),
            'answerable_total': len(answerable),
            'latency_median_seconds': statistics.median(latencies) if latencies else None,
            'system_errors': sum(bool(r.get('system_error')) for r in rows)}
