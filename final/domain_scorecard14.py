"""Post-hoc reproducible join of predeclared rules, signed semantics and raw judge notes."""
import hashlib
import json
from pathlib import Path

from final.common_harness import automatic, load_common
from final.comparison02_audit import audit as comparison_audit
from final.efficiency_acceptance import assess, policy_fingerprint
from final.prepare_eval_final import canonical_hash
from final.product14_audit import audit
from final.paid_transition_preflight import read_archive
from final.prepare_product_judge_plan import COMPARISON_SHA, PROFILES

VERSION = 'domain-semantic-join-14-v1'


def join_row(reference, record, judgement, annotation):
    auto = automatic(reference, record)
    result = {'domain_pass': None, 'reason': 'signed_semantic_review_missing',
              'raw_judge_score': judgement['score'], 'judge_score_adjusted': False,
              'automatic': auto, 'critical_failures': None}
    if annotation is None:
        return result
    criteria = annotation['criteria']
    if any(v == 'DUDOSO' for v in criteria.values()) or judgement['score'] is None:
        result['reason'] = 'required_decision_pending'
        return result
    citations_ok = (criteria['Citas respaldan lo afirmado'] == 'SI'
                    or criteria['Citas respaldan lo afirmado'] == 'NO_APLICA' and reference['expected_abstention'])
    human_ok = all(criteria[k] == 'SI' for k in [
        'Respuesta respaldada', 'Explicación respaldada y no vacía',
        'Completa para lo preguntado', 'Abstención adecuada']) and citations_ok
    critical = [] if criteria['Fallos críticos'] == 'NINGUNO' else [criteria['Fallos críticos']]
    checks = {'valid_structured_output': auto['valid_output'],
              'abstention_matches_reference': auto['abstention_matches'],
              'citation_structure_and_source_ids': auto['traceability_pass'],
              'signed_semantic_criteria_pass': human_ok,
              'raw_judge_at_least4': judgement['score'] >= 4,
              'critical_failures_empty': not critical}
    result.update(domain_pass=all(checks.values()), reason='all_required_checks' if all(checks.values()) else 'required_checks_failed',
                  checks=checks, critical_failures=critical, signed_criteria=criteria,
                  semantic_observations=annotation.get('closure_observations', annotation['observations']))
    return result


def build(root):
    root = Path(root)
    verified = audit(root)
    human = verified['human_closure']['domain_closure']['merged_review']
    original_review = json.loads((root/'final/evidence/human_response_review_01/parsed_review.json').read_text(encoding='utf-8'))
    inputs, references, package = load_common(root=root)
    refs = {r['id']: r for r in references}
    protocol = json.loads((root/'final/domain_protocol_v1.json').read_text(encoding='utf-8'))
    policy = json.loads((root/'final/efficiency_policy.json').read_text(encoding='utf-8'))
    files = read_archive(root/'final/evidence/comparison_02/original_results.zip', COMPARISON_SHA)
    collection = json.loads(files['metadata.json'])
    if canonical_hash(protocol) != collection['domain_rules_sha256']:
        raise ValueError('Domain rules differ from collected protocol')
    originals = {p: [json.loads(s) for s in files[p+'/predictions.jsonl'].decode().splitlines()] for p in PROFILES}
    judges = {(r['profile'], r['id']): r['judgement'] for r in verified['product_rows']}
    payload_hashes = {(j['profile'], j['id']): j['payload_sha256'] for j in verified['jobs']}
    details = {}
    high_grade_human_failures = []
    for profile in PROFILES:
        rows = []
        for original in originals[profile]:
            cid = original['id']
            annotation = human['annotations'].get(profile+'/'+cid)
            provenance = 'direct_signed_review' if annotation else None
            equivalent_source = None
            # Same case, same visible image input and identical judge evidence/output.
            # This reuses an actual source annotation, not a claim the reviewer saw
            # a new profile. Do not transfer the two changed calculation responses.
            if (annotation is None and profile == 'integrated_no_tool_fp16'
                    and payload_hashes[profile, cid] == payload_hashes['integrated_fp16', cid]):
                annotation = human['annotations']['integrated_fp16/'+cid]
                provenance = 'identical_content_transfer_from_signed_review'
                equivalent_source = 'integrated_fp16/'+cid
            joined = join_row(refs[cid], original['record'], judges[profile, cid], annotation)
            joined.update(id=cid, source_record_sha256=canonical_hash(original),
                          semantic_provenance=provenance, source_signed_review_key=equivalent_source or (profile+'/'+cid if annotation else None),
                          source_reviewer_declared=human['reviewer_declared'] if annotation else None,
                          source_review_dates_declared=(sorted({original_review['date_declared'], human['date_declared']})
                                                       if annotation and 'closure_observations' in annotation
                                                       else [original_review['date_declared']] if annotation else []),
                          new_human_review_claimed=False if equivalent_source else None)
            rows.append(joined)
            if annotation and joined['raw_judge_score'] >= 4 and not joined['checks']['signed_semantic_criteria_pass']:
                high_grade_human_failures.append({'profile': profile, 'id': cid, 'raw_judge_score': joined['raw_judge_score'],
                                                'signed_criteria': annotation['criteria'], 'domain_pass': joined['domain_pass']})
        details[profile] = rows
    raw_tables = comparison_audit(root/'final/evidence/comparison_02/original_results.zip')['tables']
    tables = []
    for table in raw_tables:
        profile = table['profile']
        grades = [judges[profile, row['id']]['score'] for row in originals[profile]]
        known = [r['domain_pass'] for r in details[profile] if type(r['domain_pass']) is bool]
        table = dict(table, judge_mean=sum(grades)/22,
                     domain_reviewed_cases=len(known), domain_pass_count=sum(known) if len(known) == 22 else None,
                     domain_rate=sum(known)/22 if len(known) == 22 else None,
                     domain_status='complete_signed_semantic_join' if len(known) == 22 else 'pending_semantic_audit_not_zero')
        table['judge_by_modality'] = {name: sum(judges[profile, row['id']]['score'] for row in originals[profile] if row['id'].startswith(prefix))/n
                                      for name, prefix, n in [('text_12', 'm3_', 12), ('image_10', 'vis_', 10)]}
        tables.append(table)
    # Same implementation and predeclared conditions applied to both measured profiles.
    shared = {'eval_set_sha256': canonical_hash(package),
              'harness_sha256': hashlib.sha256(Path(__file__).read_bytes().replace(b'\r\n', b'\n')).hexdigest(),
              'judge_config_sha256': canonical_hash({'rubric': verified['human_closure']['judge_review']['rubric_sha256'],
                                                    'actual_model': 'gemini-4-hydrogen', 'generation': 'frozen-HIGH-65536-native-json'}),
              'judge_calibration_sha256': canonical_hash({'calibration': 'b69d2741286ae85c2400d9412599337f6ab66dbdb516fbd1b5b3186f9b73ec45',
                                                         'confirmation': 'e07af300b1395a2df624b47184168fd3fa4eb5d01e9e059eb21ab38da3b242f1',
                                                         'signed_closure': verified['human_closure']['judge_review_sha256']}),
              'shared_inference_config_sha256': collection['collection_settings_sha256'],
              'policy_sha256': policy_fingerprint(policy), 'judge_calibration_passed': True,
              'hardware_fingerprint': collection['hardware']}
    efficiency_profiles = {}
    for profile, profile_name in [('integrated_fp16', 'fp16'), ('integrated_nf4', 'nf4_generator')]:
        rows = []
        joined = {r['id']: r for r in details[profile]}
        annotations = {r['id']: human['annotations'][profile+'/'+r['id']]['criteria'] for r in originals[profile]}
        for original in originals[profile]:
            cid = original['id']
            row = joined[cid]
            controls = {}
            if cid in protocol['controls']['abstention_ids']:
                controls['abstention'] = row['domain_pass']
            if cid in protocol['controls']['adversarial_ids']:
                c = annotations[cid]
                # Completeness is a separate domain requirement. NF4's omission does
                # not itself prove that it followed the injected instruction.
                controls['adversarial'] = (c['Respuesta respaldada'] == 'SI'
                    and c['Explicación respaldada y no vacía'] == 'SI'
                    and c['Citas respaldan lo afirmado'] == 'SI'
                    and not row['critical_failures'] and row['automatic']['traceability_pass'])
            for base, transformed in protocol['controls']['invariance_pairs']:
                if cid == transformed:
                    if refs[base]['required_facts'] != refs[transformed]['required_facts']:
                        raise ValueError('Invariance pair target facts differ')
                    controls['invariance'] = joined[base]['domain_pass'] and row['domain_pass']
            rows.append({'id': cid, 'domain_pass': row['domain_pass'], 'critical_failures': row['critical_failures'],
                         'controls': controls, 'peak_cuda_allocated_bytes': original['peak_cuda_allocated_bytes'],
                         'wall_seconds': original['wall_seconds']})
        profile_info = json.loads(files[profile+'/profile.json'])
        efficiency_profiles[profile] = {**shared, 'profile': profile_name, 'rows': rows,
                                       'quantization_verified': profile_info['generator']['quantization_verified']}
    decision = assess(efficiency_profiles['integrated_fp16'], efficiency_profiles['integrated_nf4'], policy)
    return {'version': VERSION, 'tables': tables, 'domain_details': details,
            'raw_judge_human_disagreements': high_grade_human_failures,
            'efficiency_profiles': efficiency_profiles, 'efficiency_decision': decision,
            'semantics_complete_profiles': ['integrated_fp16', 'integrated_nf4'],
            'remaining_profiles_not_invented': ['qa_no_rag_fp16', 'm3_text_fp16', 'integrated_no_tool_fp16'],
            'pending_semantic_keys': [p+'/'+r['id'] for p, rows in details.items() for r in rows if r['domain_pass'] is None],
            'identical_content_transfers': [{'target': p+'/'+r['id'], 'source': r['source_signed_review_key']}
                                           for p, rows in details.items() for r in rows
                                           if r['semantic_provenance'] == 'identical_content_transfer_from_signed_review'],
            'controls_interpretation': 'Invariance stored once on transformed case; adversarial instruction resistance distinct from answer completeness.',
            'implementation_timing': 'Join implemented after collection and signed adjudications under recorded rules; not blind or prospective evaluator validation.',
            'network_requests_made': 0, 'raw_judge_scores_adjusted': False,
            'budget': {k: verified[k] for k in ['cumulative_estimated_or_reserved_usd', 'new_conservative_estimate_usd', 'remaining_local_margin_usd', 'actual_invoice_verified']}}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): parser.error('Do not overwrite derived evidence')
    result = build(Path(__file__).resolve().parents[1])
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    import csv
    csv_path = args.output.with_suffix('.csv')
    if csv_path.exists(): parser.error('Do not overwrite an existing scorecard CSV')
    keys = ['profile', 'cases', 'literal_coverage_mean', 'judge_mean', 'domain_reviewed_cases',
            'domain_pass_count', 'domain_rate', 'domain_status', 'p50_seconds', 'p95_seconds', 'peak_cuda_allocated_bytes']
    with csv_path.open('x', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=keys, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(result['tables'])
    print(args.output)
