"""Read-only arithmetic over the public corpus, never over evaluation references."""
from decimal import Decimal, InvalidOperation, localcontext
import re
import time

TOOL_NAME = 'diferencia_valores_contratos'
TOOL_SCHEMA = {
    'name': TOOL_NAME,
    'description': 'Consulta valores registrados de dos fichas por ID y calcula su diferencia absoluta en COP. No determina sobrecostos ni irregularidades.',
    'parameters': {
        'type': 'object',
        'properties': {k: {'type': 'string', 'pattern': r'^CO1\.PCCNTR\.[0-9]+$'}
                       for k in ['id_a', 'id_b']},
        'required': ['id_a', 'id_b'], 'additionalProperties': False,
    },
}


class ContractTools:
    def __init__(self, documents, timeout_seconds=2.0):
        if timeout_seconds <= 0:
            raise ValueError('Timeout must be positive')
        self.documents = {d['doc_id']: d for d in documents}
        if len(self.documents) != len(documents):
            raise ValueError('Duplicate document ID')
        self.timeout_seconds = timeout_seconds

    def execute(self, name, arguments, allowed_ids):
        start = time.perf_counter()
        def expired():
            if time.perf_counter() - start > self.timeout_seconds:
                raise TimeoutError('Local tool time budget exceeded')
        try:
            if name != TOOL_NAME:
                raise ValueError('Unknown tool')
            if not isinstance(arguments, dict) or set(arguments) != {'id_a', 'id_b'}:
                raise ValueError('Expected exactly id_a and id_b')
            ids = [arguments['id_a'], arguments['id_b']]
            if any(not isinstance(i, str) or not re.fullmatch(r'CO1\.PCCNTR\.[0-9]+', i) for i in ids):
                raise ValueError('Invalid contract identifier')
            if ids[0] == ids[1]:
                raise ValueError('Two different contracts required')
            if not set(ids).issubset(allowed_ids):
                raise ValueError('Tool IDs must appear explicitly in the question')
            contexts, values = [], []
            for doc_id in ids:
                expired()
                if doc_id not in self.documents:
                    raise ValueError('Contract not present in source snapshot: ' + doc_id)
                doc = self.documents[doc_id]
                matches = list(re.finditer(r'^Valor del contrato \(COP\): ([^\r\n]+)', doc['text'], re.MULTILINE))
                if len(matches) != 1:
                    raise ValueError('Missing or ambiguous source value: ' + doc_id)
                match = matches[0]
                literal = match.group(1).strip()
                if not re.fullmatch(r'[0-9]+(?:\.[0-9]+)?', literal):
                    raise ValueError('Source value is not an unambiguous decimal')
                value = Decimal(literal)
                if not value.is_finite() or len(literal) > 32:
                    raise ValueError('Invalid source amount')
                values.append(value)
                contexts.append({'chunk_id': doc_id+'::tool_value', 'doc_id': doc_id,
                                 'text': match.group(0), 'start_char': match.start(),
                                 'end_char': match.end(), 'source_url': doc['source_url'],
                                 'evidence_type': 'source_field'})
            expired()
            with localcontext() as ctx:
                ctx.prec = 70
                difference = abs(values[0] - values[1])
            # Decimal strings preserve exact arithmetic and are JSON serializable.
            return {'ok': True, 'name': name, 'arguments': arguments,
                    'values_cop': {i: format(v, 'f') for i, v in zip(ids, values)},
                    'absolute_difference_cop': format(difference, 'f'),
                    'operation': f'abs({values[0]} - {values[1]}) = {difference} COP',
                    'contexts': contexts, 'error': None,
                    'latency_seconds': time.perf_counter()-start}
        except (ValueError, InvalidOperation, TimeoutError) as exc:
            return {'ok': False, 'name': name, 'arguments': arguments, 'contexts': [],
                    'error': str(exc), 'latency_seconds': time.perf_counter()-start}
