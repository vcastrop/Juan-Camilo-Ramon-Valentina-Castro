"""RAGAS metrics computed by hand, following the S10 lab, with a local LLM judge.

This is NOT the `ragas` library. Same four definitions (faithfulness, answer relevancy,
context precision, context recall), local Qwen as judge and the index embedding model for
answer relevancy. Every judge call, its raw output and parse result are kept.
"""
import re
import statistics
import unicodedata

RAGAS_VERSION = 'm3-ragas-lab-1.0'
YES_NO_SYSTEM = 'Responde solo sí o no.'
QUESTION_SYSTEM = 'Genera SOLO la pregunta que esta respuesta contestaría, sin nada más.'
APPLICABILITY = {
    'faithfulness': 'Salida válida y abstencion=false (una abstención no hace afirmaciones que verificar).',
    'answer_relevancy': 'Salida válida en pregunta respondible.',
    'context_precision': 'Pregunta respondible con al menos un contexto entregado al generador.',
    'context_recall': 'Pregunta respondible con al menos un contexto entregado al generador.',
}


def _plain(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text.casefold())
                   if unicodedata.category(c) != 'Mn')


def parse_yes_no(raw):
    """Strict: the first word must be sí/si/yes/no. Anything else is a parse failure (None)."""
    words = re.findall(r'[a-z]+', _plain(raw or ''))
    if not words:
        return None
    return {'si': 1, 'yes': 1, 'no': 0}.get(words[0])


def split_statements(text):
    # Do not split decimal or thousand separators inside numbers (250.000.000).
    parts = re.split(r'(?<!\d)[.;\n]+|[.;\n]+(?!\d)', text or '')
    return [p.strip() for p in parts if len(p.strip()) > 12]


def context_text(contexts, tools=()):
    lines = [f"[{c['chunk_id']}] {c['text']}" for c in contexts]
    lines += [f"[calculo] {t['operation']}" for t in tools]
    return '\n'.join(lines)


def tool_results(record):
    return [e['tool_result'] for e in record.get('tool_trace', [])
            if e.get('tool_result') and e['tool_result'].get('ok')]


class LabRagas:
    def __init__(self, generator, encoder):
        self.generator, self.encoder = generator, encoder

    def _ask(self, system, user, calls):
        raw = self.generator.generate(system, user)
        verdict = parse_yes_no(raw) if system == YES_NO_SYSTEM else None
        calls.append({'system': system, 'user': user, 'raw': raw, 'verdict': verdict})
        return raw, verdict

    def faithfulness(self, record, calls):
        output = record['output']
        context = context_text(record['contexts'], tool_results(record))
        claims = split_statements(f"{output['respuesta']}. {output['explicacion']}")
        verdicts = []
        for claim in claims:
            _, v = self._ask(YES_NO_SYSTEM, f'Contexto:\n{context}\n\n¿El contexto respalda esta afirmación? "{claim}"', calls)
            verdicts.append(v)
        valid = [v for v in verdicts if v is not None]
        return {'value': sum(valid)/len(valid) if valid else None, 'statements': len(claims),
                'valid_verdicts': len(valid)}

    def answer_relevancy(self, record, calls):
        raw, _ = self._ask(QUESTION_SYSTEM, record['output']['respuesta'], calls)
        if not raw or not raw.strip():
            return {'value': None, 'generated_question': raw}
        import numpy as np
        a, b = self.encoder.encode([record['question'], raw.strip()])
        value = float(np.dot(a, b)/(np.linalg.norm(a)*np.linalg.norm(b)))
        return {'value': value, 'generated_question': raw.strip()}

    def context_precision(self, record, reference, calls):
        # RAGAS definition: rank-aware average precision of the useful contexts.
        relevance = []
        for c in record['contexts']:
            _, v = self._ask(YES_NO_SYSTEM, f'Pregunta: {record["question"]}\nRespuesta de referencia: {reference}\n\n'
                             f'¿Este pasaje es útil para llegar a la respuesta de referencia? "{c["text"]}"', calls)
            relevance.append(v)
        valid = [v for v in relevance if v is not None]
        if not valid:
            return {'value': None, 'relevance': relevance, 'simple_fraction': None}
        hits, total = 0, 0.0
        for rank, v in enumerate(relevance, 1):  # original rank; unparsed verdicts count as not useful
            if v:
                hits += 1
                total += hits/rank
        return {'value': total/hits if hits else 0.0, 'relevance': relevance,
                'simple_fraction': sum(valid)/len(valid)}

    def context_recall(self, record, reference, calls):
        context = context_text(record['contexts'], tool_results(record))
        sentences = split_statements(reference) or [reference]
        verdicts = []
        for s in sentences:
            _, v = self._ask(YES_NO_SYSTEM, f'Contexto:\n{context}\n\n¿Esta afirmación de referencia se puede atribuir al contexto? "{s}"', calls)
            verdicts.append(v)
        valid = [v for v in verdicts if v is not None]
        return {'value': sum(valid)/len(valid) if valid else None, 'sentences': len(sentences),
                'valid_verdicts': len(valid)}

    def evaluate(self, case, record):
        """Return per-metric dicts; inapplicable metrics are explicit N/A, never 0 or 1."""
        output, calls = record.get('output'), []
        answerable = case['kind'] != 'unanswerable'
        has_context = bool(record.get('contexts'))
        na = lambda why: {'value': None, 'na': why}
        result = {'eval_id': case['eval_id'], 'variant': record.get('variant'), 'kind': case['kind']}
        if not isinstance(output, dict):
            for m in APPLICABILITY:
                result[m] = na('salida_invalida')
        else:
            result['faithfulness'] = na('abstencion') if output['abstencion'] else self.faithfulness(record, calls)
            result['answer_relevancy'] = self.answer_relevancy(record, calls) if answerable else na('no_respondible')
            for m, fn in [('context_precision', self.context_precision), ('context_recall', self.context_recall)]:
                if not answerable:
                    result[m] = na('no_respondible')
                elif not has_context:
                    result[m] = na('sin_contexto')
                else:
                    result[m] = fn(record, case['expected'], calls)
        doc_ids = {c['doc_id'].upper() for c in record.get('contexts', [])}
        # Deterministic retrieval check (not RAGAS): were the gold source records delivered?
        result['source_hit'] = ({s.upper() for s in case['source_ids']}.issubset(doc_ids)
                                if answerable else None)
        result['judge_calls'] = calls
        result['judge_parse_failures'] = sum(c['system'] == YES_NO_SYSTEM and c['verdict'] is None for c in calls)
        return result


def summarize(results):
    summary = {'ragas_version': RAGAS_VERSION, 'cases': len(results)}
    for m in APPLICABILITY:
        values = [r[m]['value'] for r in results if r[m].get('value') is not None]
        summary[m] = statistics.mean(values) if values else None
        summary[m+'_n'] = len(values)
        summary[m+'_na'] = sum('na' in r[m] for r in results)
    hits = [r['source_hit'] for r in results if r['source_hit'] is not None]
    summary['source_hit_rate'] = sum(hits)/len(hits) if hits else None
    summary['judge_calls'] = sum(len(r['judge_calls']) for r in results)
    summary['judge_parse_failures'] = sum(r['judge_parse_failures'] for r in results)
    return summary
