"""Compare unambiguous source fields, never gold; agreement is not authenticity."""
from decimal import Decimal
import re
import unicodedata

LABELS = {'valor_cop':'Valor del contrato (COP):', 'modalidad':'Modalidad de contratación:'}


def modality_key(value):
    return ' '.join(''.join(c for c in unicodedata.normalize('NFD',value.casefold())
                           if not unicodedata.combining(c)).split())


def amount_key(value):
    # Snapshot and parser expose canonical decimal strings. No float, grouping guesses or digit repair.
    if not isinstance(value,str) or not re.fullmatch(r'\d+(?:\.\d+)?',value):
        return None
    return Decimal(value)


def compare_visual_source(visual, document):
    report = {'status':'not_comparable', 'source_id':None, 'compared_fields':[],
              'conflicts':[], 'unverifiable_fields':[],
              'scope':'Only amount/modality for matching ID in frozen snapshot; neither document authenticity nor OCR truth verified.'}
    if not document or not visual.get('id_contrato') or document['doc_id'] != visual['id_contrato']:
        return report
    report['source_id'] = document['doc_id']
    for key,label in LABELS.items():
        observed = visual.get(key)
        if observed is None:
            continue
        literals = [s[len(label):].strip() for s in document['text'].splitlines() if s.startswith(label)]
        if len(literals) != 1 or not literals[0] or not isinstance(observed,str):
            report['unverifiable_fields'].append(key)
            continue
        source = literals[0]
        if key == 'valor_cop':
            left,right = amount_key(observed),amount_key(source)
            if left is None or right is None:
                report['unverifiable_fields'].append(key)
                continue
        else:
            left,right = modality_key(observed),modality_key(source)
        report['compared_fields'].append(key)
        if left != right:
            report['conflicts'].append({'field':key,'visual_value':observed,'snapshot_value':source})
    if report['conflicts']:
        report['status'] = 'conflict'
    elif report['compared_fields']:
        report['status'] = 'partial_agreement' if report['unverifiable_fields'] else 'agreement_on_compared_fields'
    return report


def conflict_explanation(report):
    parts=[]
    for c in report['conflicts']:
        name='valor (COP)' if c['field']=='valor_cop' else 'modalidad'
        parts.append(f"{name}: lectura visual «{c['visual_value']}»; snapshot «{c['snapshot_value']}»")
    return ('Hay una discrepancia entre la lectura de la imagen y el snapshot para '+report['source_id']+
            ': '+'; '.join(parts)+'. No se confirma cuál es correcto. Revise la imagen original y la fecha/versión de la ficha; puede ser un error de lectura o una diferencia entre documentos.')
