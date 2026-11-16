"""Tool eligibility from user question only, independent of references or scores."""
import re
from final.integration import contract_ids, normalized


def eligible_difference(question):
    q = normalized(question)
    if len(contract_ids(question)) != 2:
        return False
    if re.search(r'\b(no|sin)\s+(calcular|calcules|comparar|compares|usar|uses)\b', q):
        return False
    return bool(re.search(r'\bdiferencia\b', q) and re.search(r'\b(valores?|montos?|importes?)\b', q))
