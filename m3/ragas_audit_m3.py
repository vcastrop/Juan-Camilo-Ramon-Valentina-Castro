"""Versioned evaluator repair; does not alter original RAGAS evidence.

Uses the same applicability policy and prompts as 1.0, but preserves IDs in
statements, rejects ambiguous yes/no outputs, and never drops failed verdicts
from within a case. This does not establish the semantic reliability of Qwen.
"""
import re
from ragas_m3 import LabRagas, YES_NO_SYSTEM, _plain, context_text, tool_results

VERSION = 'm3-ragas-audit-1.1'


def split_statements(text):
    # A dot inside CO1.PCCNTR.123::c001, 2.5 or 250.000.000 is not a boundary.
    return [s.strip() for s in re.split(r'[;\n]+|(?<=[.!?])\s+', text or '')
            if s.strip() and re.search(r'\w', s)]


def parse_yes_no(raw):
    value = re.sub(r'[.!]+$', '', _plain(raw or '').strip()).strip()
    return {'si': 1, 'yes': 1, 'no': 0}.get(value)


def aggregate(verdicts):
    return sum(verdicts)/len(verdicts) if verdicts and all(v is not None for v in verdicts) else None


class AuditedRagas(LabRagas):
    def _ask(self, system, user, calls):
        raw = self.generator.generate(system, user)
        verdict = parse_yes_no(raw) if system == YES_NO_SYSTEM else None
        calls.append({'system': system, 'user': user, 'raw': raw, 'verdict': verdict})
        return raw, verdict

    def faithfulness(self, record, calls):
        output = record['output']
        context = context_text(record['contexts'], tool_results(record))
        claims = split_statements(f"{output['respuesta']}. {output['explicacion']}")
        verdicts = [self._ask(YES_NO_SYSTEM, f'Contexto:\n{context}\n\n¿El contexto respalda esta afirmación? "{c}"', calls)[1]
                    for c in claims]
        return {'value': aggregate(verdicts), 'statements': len(claims), 'claims': claims,
                'verdicts': verdicts, 'valid_verdicts': sum(v is not None for v in verdicts)}

    def context_recall(self, record, reference, calls):
        context = context_text(record['contexts'], tool_results(record))
        claims = split_statements(reference)
        verdicts = [self._ask(YES_NO_SYSTEM, f'Contexto:\n{context}\n\n¿Esta afirmación de referencia se puede atribuir al contexto? "{c}"', calls)[1]
                    for c in claims]
        return {'value': aggregate(verdicts), 'sentences': len(claims), 'claims': claims,
                'verdicts': verdicts, 'valid_verdicts': sum(v is not None for v in verdicts)}

    def context_precision(self, record, reference, calls):
        result = super().context_precision(record, reference, calls)
        if any(v is None for v in result['relevance']):
            result.update(value=None, simple_fraction=None)
        return result
