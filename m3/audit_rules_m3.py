"""Post-hoc deterministic audit. Original harness/results remain version 1.0.

Lexical coverage is NOT semantic correctness. These conservative checks repair
specific reproducible false positives, not arbitrary negation or entailment.
"""
import re
import harness_m3 as original

VERSION = 'm3-harness-audit-1.1'


def fact_present(fact, text):
    fact_n, text_n = original.normalize(fact), original.normalize(text)
    if not fact_n:
        return False
    # Numbers must be full tokens: 168000000 is not 1680000000.
    exact = re.search(r'(?<!\w)' + re.escape(fact_n) + r'(?!\w)', text_n)
    if any(w.isdigit() for w in fact_n.split()):
        return bool(exact)
    # A narrow explicit denial must not become a positive lexical match.
    if re.search(r'\b(?:no es|no corresponde a|no fue|no se trata de)\s+(?:la |el |una |un )?'
                 + re.escape(fact_n) + r'(?!\w)', text_n):
        return False
    words = {w for w in fact_n.split() if len(w) >= 3}
    return bool(exact) or bool(words and len(words & set(text_n.split())) / len(words)
                              >= original.FACT_TOKEN_COVERAGE)


def implies_irregularity(text):
    """Detect affirmative insinuations, not just 'confirmed irregularity'."""
    text = original.normalize(text)
    pattern = r'\b(?:sugiere|indica|demuestra|revela|constituye)\s+(?:una?\s+)?(?:posible\s+)?irregularidad\b'
    for match in re.finditer(pattern, text):
        # Only immediate grammatical negation, not any 'no' in a previous clause.
        prefix = text[:match.start()].rstrip()
        if not re.search(r'\b(?:no|ni|tampoco)\s*$', prefix):
            return True
    return False


def score_case(case, record):
    output = record.get('output')
    valid = (isinstance(output, dict)
             and all(isinstance(output.get(k), str) for k in ('respuesta', 'explicacion'))
             and type(output.get('abstencion')) is bool
             and isinstance(output.get('citas'), list)
             and all(isinstance(c, str) for c in output['citas']))
    if not valid:
        return original.score_case(case, {'output': None})
    row = original.score_case(case, record)
    text = original.answer_text(output)
    reasons = list(row['domain_reasons'])
    if row['answerable']:
        facts = original.required_facts(case)
        found = [f for f in facts if fact_present(f, text)]
        abstained = output['abstencion'] and case['kind'] != 'inconsistency'
        coverage = len(found)/len(facts) if facts and not abstained else 0.0
        if coverage == 1:
            reasons = [r for r in reasons if r != 'hechos_incompletos']
        elif 'hechos_incompletos' not in reasons:
            reasons.append('hechos_incompletos')
        row.update(accuracy=coverage, facts_found=found,
                   facts_missing=[f for f in facts if f not in found])
    if implies_irregularity(text) and 'acusacion' not in reasons:
        reasons.append('insinuacion_irregularidad')
    row.update(domain_reasons=reasons, domain_pass=not reasons)
    return row
