"""RAGAS m3-ragas-lab-1.1: fixes statement segmentation and adds the exact S10 lab variants.

1.0 split 'CO1.PCCNTR.1109703' at its dots, creating artificial statements. 1.1 splits only at
sentence punctuation followed by whitespace/end. Reported metrics:
- lab (exact S10 formulas and prompts): faithfulness, answer_relevancy, context_precision_lab
  (fraction of passages judged relevant to the QUESTION), context_recall_lab (one yes/no: does the
  context contain what is needed for the whole reference);
- adaptation kept from 1.0 for comparison: context_precision_rank (rank-weighted, useful for the
  reference) and context_recall_segment (fraction of reference sentences attributable).
"""
import re
import statistics
from ragas_m3 import LabRagas, YES_NO_SYSTEM, context_text, tool_results

RAGAS_VERSION = 'm3-ragas-lab-1.1'
METRICS = ['faithfulness', 'answer_relevancy', 'context_precision_lab', 'context_recall_lab',
           'context_precision_rank', 'context_recall_segment']
APPLICABILITY = {
    'faithfulness': 'Salida válida y abstencion=false.',
    'answer_relevancy': 'Salida válida en pregunta respondible.',
    'context_precision_lab': 'Respondible con contexto.', 'context_recall_lab': 'Respondible con contexto.',
    'context_precision_rank': 'Respondible con contexto.', 'context_recall_segment': 'Respondible con contexto.',
}


def split_statements(text):
    """Sentence split that keeps identifiers (CO1.PCCNTR.1), chunk ids and numbers (250.000.000) intact."""
    parts = re.split(r'[.!?]+(?=\s|$)|[;\n]+', text or '')
    return [p.strip() for p in parts if len(p.strip()) > 12]


class LabRagasV11(LabRagas):
    def faithfulness(self, record, calls):
        output = record['output']
        context = context_text(record['contexts'], tool_results(record))
        claims = split_statements(f"{output['respuesta']}. {output['explicacion']}")
        verdicts = [self._ask(YES_NO_SYSTEM, f'Contexto:\n{context}\n\n¿El contexto respalda esta afirmación? "{c}"', calls)[1]
                    for c in claims]
        valid = [v for v in verdicts if v is not None]
        return {'value': sum(valid)/len(valid) if valid else None, 'statements': len(claims),
                'claims': claims, 'valid_verdicts': len(valid)}

    def context_precision_lab(self, record, calls):
        verdicts = [self._ask(YES_NO_SYSTEM, f'Pregunta: {record["question"]}\n\n¿Este pasaje es relevante para responderla? "{c["text"]}"', calls)[1]
                    for c in record['contexts']]
        valid = [v for v in verdicts if v is not None]
        return {'value': sum(valid)/len(valid) if valid else None, 'relevance': verdicts}

    def context_recall_lab(self, record, reference, calls):
        context = context_text(record['contexts'], tool_results(record))
        _, v = self._ask(YES_NO_SYSTEM, f'Contexto:\n{context}\n\n¿El contexto contiene lo necesario para llegar a esta referencia? "{reference}"', calls)
        return {'value': None if v is None else float(v)}

    def context_recall(self, record, reference, calls):
        context = context_text(record['contexts'], tool_results(record))
        sentences = split_statements(reference) or [reference]
        verdicts = [self._ask(YES_NO_SYSTEM, f'Contexto:\n{context}\n\n¿Esta afirmación de referencia se puede atribuir al contexto? "{s}"', calls)[1]
                    for s in sentences]
        valid = [v for v in verdicts if v is not None]
        return {'value': sum(valid)/len(valid) if valid else None, 'sentences': len(sentences), 'valid_verdicts': len(valid)}

    def evaluate(self, case, record):
        output, calls = record.get('output'), []
        answerable = case['kind'] != 'unanswerable'
        na = lambda why: {'value': None, 'na': why}
        result = {'eval_id': case['eval_id'], 'variant': record.get('variant'), 'kind': case['kind']}
        if not isinstance(output, dict):
            for m in METRICS:
                result[m] = na('salida_invalida')
        else:
            result['faithfulness'] = na('abstencion') if output['abstencion'] else self.faithfulness(record, calls)
            result['answer_relevancy'] = self.answer_relevancy(record, calls) if answerable else na('no_respondible')
            context_metrics = {
                'context_precision_lab': lambda: self.context_precision_lab(record, calls),
                'context_recall_lab': lambda: self.context_recall_lab(record, case['expected'], calls),
                'context_precision_rank': lambda: self.context_precision(record, case['expected'], calls),
                'context_recall_segment': lambda: self.context_recall(record, case['expected'], calls)}
            for m, fn in context_metrics.items():
                if not answerable:
                    result[m] = na('no_respondible')
                elif not record.get('contexts'):
                    result[m] = na('sin_contexto')
                else:
                    result[m] = fn()
        result['judge_calls'] = calls
        result['judge_parse_failures'] = sum(c['system'] == YES_NO_SYSTEM and c['verdict'] is None for c in calls)
        return result


def summarize(results):
    summary = {'ragas_version': RAGAS_VERSION, 'cases': len(results)}
    for m in METRICS:
        values = [r[m]['value'] for r in results if r[m].get('value') is not None]
        summary[m] = statistics.mean(values) if values else None
        summary[m+'_n'] = len(values)
    summary['judge_calls'] = sum(len(r['judge_calls']) for r in results)
    summary['judge_parse_failures'] = sum(r['judge_parse_failures'] for r in results)
    return summary
