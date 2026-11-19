"""Complete domain receipt from 46 signed decisions plus one explicit chat closure."""
import copy
import csv
from datetime import date
import hashlib
import json
from pathlib import Path

from final.domain_scorecard14 import build as previous_scorecard, join_row
from final.human_response_review import parse
from final.paid_transition_preflight import read_archive
from final.prepare_eval_final import canonical_hash
from final.prepare_product_judge_plan import COMPARISON_SHA, PROFILES

REVIEW_SHA = 'f94cefd0e1c47e363dde7a89c6b510bb4a6824719ba329ee877274eabd9910cc'


def receipt(root, previous):
    root = Path(root)
    folder = root/'final/evidence/domain_review46'
    raw = (folder/'original_review.md').read_bytes()
    if hashlib.sha256(raw).hexdigest() != REVIEW_SHA:
        raise ValueError('Signed 46-case review changed')
    manifest = [{'review_key': key} for key in previous['pending_semantic_keys']]
    if len(manifest) != 46:
        raise ValueError('Original pending population differs')
    protocol = json.loads((root/'final/domain_protocol_v1.json').read_text(encoding='utf-8'))
    original = parse(raw.decode('utf-8-sig'), manifest, protocol)
    date.fromisoformat(original['date_declared'])
    decision = json.loads((folder/'chat_closure.json').read_text(encoding='utf-8'))
    expected = {'review_sha256': REVIEW_SHA, 'key': 'qa_no_rag_fp16/m3_011',
                'criterion': 'Abstención adecuada', 'original_value': 'DUDOSO', 'confirmed_value': 'NO',
                'source': 'Explicit user confirmation in this chat'}
    if any(decision.get(k) != v for k, v in expected.items()):
        raise ValueError('Explicit chat adjudication missing or changed')
    effective = copy.deepcopy(original)
    row = effective['annotations'][decision['key']]
    if row['criteria'][decision['criterion']] != 'DUDOSO':
        raise ValueError('Attempt to replace an already decided criterion')
    row['criteria'][decision['criterion']] = decision['confirmed_value']
    row['chat_closure'] = decision
    if any('DUDOSO' in r['criteria'].values() for r in effective['annotations'].values()):
        raise ValueError('Additional human doubt remains unresolved')
    effective['status'] = 'received_and_closed_by_explicit_chat_adjudication'
    return {'original_parsed_review': original, 'effective_review': effective,
            'chat_closure': decision, 'original_review_sha256': REVIEW_SHA,
            'original_file_modified': False, 'llm_scores_created_or_adjusted': False}


def build(root):
    root = Path(root)
    result = previous_scorecard(root)
    previous_domains = {(p, r['id']): r['domain_pass'] for p, rows in result['domain_details'].items() for r in rows}
    received = receipt(root, result)
    review = received['effective_review']
    files = read_archive(root/'final/evidence/comparison_02/original_results.zip', COMPARISON_SHA)
    refs = {r['id']: r for r in json.loads((root/'final/eval/common_v1/references.json').read_text(encoding='utf-8'))}
    originals = {p: {r['id']: r for r in (json.loads(s) for s in files[p+'/predictions.jsonl'].decode().splitlines())} for p in PROFILES}
    for profile, rows in result['domain_details'].items():
        for index, old in enumerate(rows):
            key = profile+'/'+old['id']
            if key not in review['annotations']:
                continue
            if old['domain_pass'] is not None:
                raise ValueError('Only previously unknown rows may be completed')
            original = originals[profile][old['id']]
            annotation = review['annotations'][key]
            joined = join_row(refs[old['id']], original['record'], {'score': old['raw_judge_score']}, annotation)
            if joined['domain_pass'] is None:
                raise ValueError('Domain row still pending')
            joined.update(id=old['id'], source_record_sha256=old['source_record_sha256'],
                          semantic_provenance='direct_signed_review46_with_separate_chat_closure',
                          source_signed_review_key=key, source_reviewer_declared=review['reviewer_declared'],
                          source_review_dates_declared=[review['date_declared']], new_human_review_claimed=None)
            if 'chat_closure' in annotation:
                joined['chat_closure'] = annotation['chat_closure']
            rows[index] = joined
    for table in result['tables']:
        rows = result['domain_details'][table['profile']]
        if len(rows) != 22 or any(type(r['domain_pass']) is not bool for r in rows):
            raise ValueError('All profiles require 22 resolved rows')
        count = sum(r['domain_pass'] for r in rows)
        table.update(domain_reviewed_cases=22, domain_pass_count=count, domain_rate=count/22,
                     domain_status='complete_signed_semantics_or_exact_equivalence')
    disagreements = []
    for profile, rows in result['domain_details'].items():
        for row in rows:
            if row['raw_judge_score'] >= 4 and row['domain_pass'] is False:
                c = row['signed_criteria']
                kind = ('semantic_support_disagreement' if c['Respuesta respaldada'] == 'NO' or c['Explicación respaldada y no vacía'] == 'NO'
                        else 'task_utility_or_completeness_vs_conditional_judge')
                disagreements.append({'profile': profile, 'id': row['id'], 'raw_judge_score': row['raw_judge_score'],
                                      'domain_pass': False, 'kind': kind, 'signed_criteria': c})
    # No historical human decisions, raw scores, inference outputs or thresholds change.
    for profile, rows in result['domain_details'].items():
        for row in rows:
            old = previous_domains[profile, row['id']]
            if old is not None and old != row['domain_pass']:
                raise ValueError('An already resolved domain decision changed')
    result.update(version='domain-semantic-closure-15-v1', review46_receipt=received,
                  semantics_complete_profiles=PROFILES, remaining_profiles_not_invented=[], pending_semantic_keys=[],
                  raw_judge_human_disagreements=disagreements,
                  semantic_coverage={'direct_signed_rows': 90, 'exact_content_transfers': 20, 'complete_rows': 110},
                  implementation_timing='Same join rules as v14; only previously missing signed decisions completed; original v14 evidence preserved.',
                  closure_adapter_sha256=hashlib.sha256(Path(__file__).read_bytes().replace(b'\r\n', b'\n')).hexdigest())
    return result


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.with_suffix('.csv').exists():
        parser.error('Do not overwrite historical or completed scorecards')
    result = build(Path(__file__).resolve().parents[1])
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    fields = ['profile', 'cases', 'literal_coverage_mean', 'judge_mean', 'domain_pass_count', 'domain_rate',
              'p50_seconds', 'p95_seconds', 'peak_cuda_allocated_bytes']
    with args.output.with_suffix('.csv').open('x', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(result['tables'])
    print(args.output)
