"""Freeze the reviewed QA set without overwriting the draft or human evidence."""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def freeze(review_path):
    raw = review_path.read_bytes()
    review = raw.decode('utf-8-sig').replace('\r\n', '\n')
    draft_path = ROOT / 'eval/eval_set_draft.json'
    draft = json.loads(draft_path.read_text(encoding='utf-8'))
    reviewer = re.search(r'^Revisor: (.+)$', review, re.M).group(1).strip()
    date = re.search(r'^Fecha de revisión: (\d{4}-\d{2}-\d{2})$', review, re.M).group(1)
    blocks = re.findall(r'## (m3_\d+) —.*?\n(.*?)(?=\n## m3_|\n# Anexo:)', review, re.S)
    by_id = dict(blocks)
    if len(blocks) != len(draft['cases']) or len(by_id) != len(blocks):
        raise ValueError('Review must cover every case exactly once')
    docs = [json.loads(line) for line in (ROOT / 'corpus/documents.jsonl').read_text(encoding='utf-8').splitlines()]
    annex = re.findall(r'```text\n(.*?)\n```', review, re.S)
    if annex != [d['text'] for d in docs]:
        raise ValueError('Review annex differs from corpus')
    for case in draft['cases']:
        block = by_id[case['eval_id']]
        if '**Pregunta:** ' + case['input'] not in block:
            raise ValueError('Question changed; explicit reconciliation required')
        decision = re.search(r'\*\*Decisión:\*\* (.+)', block).group(1).strip()
        note = block.split('**Corrección/comentario:** ', 1)[1].strip()
        if case['eval_id'] == 'm3_004':
            if decision != 'CORREGIR' or 'm3_004 aprobado condicionado a incorporar la corrección propuesta.' not in review:
                raise ValueError('Conditional approval not found')
            correction = re.search(r'Propuesta: "(.*?)"', note, re.S).group(1)
            case['expected'] = correction
            # No full truncated sentence is required for a semantically correct answer.
            case['required_facts'] = [
                'INSTITUTO DE FINANCIAMIENTO; PROMOCION Y DESARROLLO DE CALDAS',
                'intermediación de seguros para asesorar a Infi-Caldas en la contratación y administración de su programa de seguros',
            ]
            case['criterion'] += ' Aceptar paráfrasis fieles; no exigir ni inventar la continuación del texto truncado.'
            case['review_status'] = 'approved_correction_applied'
        elif decision == 'APROBADO':
            case['review_status'] = 'approved'
        else:
            raise ValueError(f'Unresolved decision: {case["eval_id"]}')
        case['reviewer'] = reviewer
        case['review_date'] = date
        case['review_notes'] = note
    draft.update(version='m3-qa-gold-1.0', status='human_reviewed',
                 authorship='AI-assisted draft reviewed by the named human; one approved correction applied',
                 review_evidence='evidence/REVISION_HUMANA_QA.md',
                 review_file_sha256=sha(raw), draft_sha256=sha(draft_path.read_bytes()),
                 corpus_sha256=sha((ROOT / 'corpus/documents.jsonl').read_bytes()))
    target = ROOT / 'eval/gold_v1'
    if target.exists():
        raise FileExistsError('Gold already exists; create a new version instead of overwriting')
    (target / 'evidence').mkdir(parents=True)
    (target / 'evidence/REVISION_HUMANA_QA.md').write_bytes(raw)
    payload = (json.dumps(draft, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    (target / 'eval_set.json').write_bytes(payload)
    manifest = {'version': draft['version'], 'count': len(draft['cases']),
                'reviewer': reviewer, 'review_date': date,
                'files': {'eval_set.json': sha(payload), 'evidence/REVISION_HUMANA_QA.md': sha(raw)},
                'corpus_sha256': draft['corpus_sha256']}
    (target / 'manifest.json').write_bytes((json.dumps(manifest, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('review', type=Path)
    freeze(parser.parse_args().review)
