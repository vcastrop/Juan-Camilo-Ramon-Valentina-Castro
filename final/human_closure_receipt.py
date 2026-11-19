"""Read actual signed decisions, retaining conditional acceptance and original files."""
import copy
from datetime import date
import hashlib
import json
from pathlib import Path
import re

from final.confirmation13_receipt import receive
from final.confirmation_final import cases
from final.human_response_review import analyze
from final.judge_final import RUBRIC, BASE_SYSTEM, rubric_fingerprint


def field(text, name):
    matches = re.findall(r'^'+re.escape(name)+r':\s*([^\r\n]+)', text, re.M)
    if len(matches) != 1:
        raise ValueError('Missing or duplicate field: '+name)
    value = matches[0].strip()
    if value == 'PENDIENTE':
        raise ValueError('Unsigned field: '+name)
    return value


def signer(text):
    name = field(text, 'Revisor/a')
    declared = field(text, 'Fecha real (AAAA-MM-DD)')
    date.fromisoformat(declared)
    return {'reviewer_declared': name, 'date_declared': declared}


def sections(text, prefix):
    result = {}
    for match in re.finditer(r'^## (.+)\r?\n([\s\S]*?)(?=^## |\Z)', text, re.M):
        key = match[1].strip()
        if key.startswith(prefix):
            if key in result:
                raise ValueError('Duplicate review section: '+key)
            result[key] = match[2]
    return result


def judge_receipt(text):
    signed = signer(text)
    reviewed = sections(text, 'confirm_')
    if set(reviewed) != {c['id'] for c in cases()}:
        raise ValueError('All twelve confirmation decisions required')
    decisions = {}
    for key, section in reviewed.items():
        value = field(section, 'Motivo aceptable')
        if value not in {'SI', 'NO', 'DUDOSO'}:
            raise ValueError('Unknown review decision')
        decisions[key] = {'declared_decision': value, 'effective_decision': value,
                          'observations': field(section, 'Observaciones')}
    conditional = decisions['confirm_empty_bad']
    # Exact explicit conditional permission in this user's signed review; not a generic
    # conversion of DUDOSO to SI or a silent change to their original annotation.
    clause = 'Si la rúbrica la contiene, el motivo es aceptable (SI).'
    condition_met = ('Sin explicación, nota máxima 2' in RUBRIC[2]
                     and 'Sin explicación, nota máxima 2' in BASE_SYSTEM)
    if conditional['declared_decision'] == 'DUDOSO' and clause in conditional['observations'] and condition_met:
        conditional.update(effective_decision='SI', resolution='explicit_user_conditional_acceptance_verified',
                           evidence=RUBRIC[2], original_decision_preserved=True)
    overall = field(text, 'Motivos de calibración aceptables (conjunto)')
    if overall not in {'SI', 'NO', 'DUDOSO'}:
        raise ValueError('Unknown calibration review decision')
    marker = 'Observaciones del anexo (si NO o DUDOSO, indicar condición/id):'
    if text.count(marker) != 1:
        raise ValueError('Missing calibration observations')
    remarks = text.split(marker, 1)[1].split('\nNo dejar SI', 1)[0].strip()
    if not remarks or remarks == 'PENDIENTE':
        raise ValueError('Missing calibration observations')
    # This fixed receipt recognises the specific condition the user also applied to
    # empty_explanation_bad. Any other outstanding doubt remains for human resolution.
    expected_condition = 'Calibración 8 (main_mitigated/empty_explanation_bad): queda DUDOSO'
    calibration_condition_resolved = (expected_condition in remarks and remarks.count('DUDOSO') == 1
                                      and conditional.get('resolution') is not None)
    calibration_ok = overall == 'SI' and calibration_condition_resolved
    approved = calibration_ok and all(d['effective_decision'] == 'SI' for d in decisions.values())
    return {**signed, 'status': 'accepted_with_documented_limits' if approved else 'human_closure_pending',
            'decisions': decisions, 'calibration_declared_decision': overall,
            'calibration_observations_verbatim': remarks,
            'calibration_empty_explanation_condition_verified': calibration_condition_resolved,
            'rubric_sha256': rubric_fingerprint(), 'judge_validated_for_task_after_technical_gates': approved,
            'scope': 'Frozen Hydrogen configuration/rubric, synthetic calibration and confirmation; not universal reliability or product correctness.',
            'human_originals_rewritten': False, 'raw_judge_scores_adjusted': False}


def domain_receipt(text, previous, summary, manifest):
    signed = signer(text)
    reviewed = sections(text, 'integrated_')
    if set(reviewed) != set(summary['open_items']):
        raise ValueError('Exactly the eight previously open records are required')
    merged = copy.deepcopy(previous)
    changes = []
    critical = {'NINGUNO', 'DUDOSO', 'central_numeric_error', 'unsupported_audit_or_fraud_claim',
                'hidden_source_conflict', 'following_untrusted_input_instructions',
                'fabricated_evidence', 'false_central_evidence_attribution'}
    for key, expected_fields in summary['open_items'].items():
        section = reviewed[key]
        justification = field(section, 'Justificación de cierre')
        supplied = re.findall(r'^Decisión — (.+?):\s*([^\r\n]+)', section, re.M)
        if len(supplied) != len(expected_fields) or {f for f, _ in supplied} != set(expected_fields):
            raise ValueError('Only the previously undecided criteria may be closed')
        for criterion, raw in supplied:
            value = raw.strip()
            allowed = critical if criterion == 'Fallos críticos' else {'SI', 'NO', 'DUDOSO'}
            if value not in allowed:
                raise ValueError('Unknown domain decision: '+value)
            old = merged['annotations'][key]['criteria'][criterion]
            if old != 'DUDOSO':
                raise ValueError('Attempt to replace an already decided criterion')
            merged['annotations'][key]['criteria'][criterion] = value
            changes.append({'key': key, 'criterion': criterion, 'previous': old,
                            'declared_decision': value, 'justification': justification})
        merged['annotations'][key]['closure_observations'] = justification
    merged.update(**signed, status='adjudicated_from_separate_signed_review')
    result = analyze(merged, manifest)
    result.update(judge_grades_available=False, domain_rate=None,
                  formal_efficiency_status='not_evaluable_product_judge_scores_pending',
                  note='Original 44-record review preserved; separate closure updates only previously DUDOSO criteria.')
    return {'signer': signed, 'changes': changes, 'merged_review': merged, 'summary': result}


def receive_closure(root):
    root = Path(root)
    technical = receive(root)
    folder = root/'final/evidence/human_closure_19'
    judge_raw = (folder/'original_judge_review.md').read_bytes()
    domain_raw = (folder/'original_domain_closure.md').read_bytes()
    judge = judge_receipt(judge_raw.decode('utf-8-sig'))
    original = json.loads((root/'final/evidence/human_response_review_01/parsed_review.json').read_text(encoding='utf-8'))
    summary = json.loads((root/'final/evidence/human_response_review_01/summary.json').read_text(encoding='utf-8'))
    manifest = json.loads((root/'final/eval/review_comparison02/manifest.json').read_text(encoding='utf-8'))
    domain = domain_receipt(domain_raw.decode('utf-8-sig'), original, summary, manifest)
    domain['summary']['judge_validated'] = judge['judge_validated_for_task_after_technical_gates']
    return {'version': 'signed-human-closure-receipt-1',
            'judge_review_sha256': hashlib.sha256(judge_raw).hexdigest(),
            'domain_closure_sha256': hashlib.sha256(domain_raw).hexdigest(),
            'technical_confirmation': technical, 'judge_review': judge, 'domain_closure': domain,
            'new_api_calls': 0, 'product_scores_created': False, 'authorized_ceiling_usd': '5.00'}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = json.dumps(receive_closure(Path(__file__).resolve().parents[1]), ensure_ascii=False, indent=2)+'\n'
    if args.output:
        if args.output.exists():
            parser.error('Do not overwrite received or derived evidence')
        args.output.write_text(result, encoding='utf-8')
        print(args.output)
    else:
        print(result)
