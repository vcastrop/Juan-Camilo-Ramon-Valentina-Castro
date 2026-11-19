"""Prepare all 110 saved outputs for evaluation; no provider calls, no dispatch authorization."""
from decimal import Decimal
import json
from pathlib import Path

from final.human_closure_receipt import receive_closure
from final.paid_transition_preflight import read_archive
from m3.judge import evidence_payload
from final.prepare_eval_final import canonical_hash

COMPARISON_SHA = '34a5b0616c77b790489d3ecf37469cf312a0de6ea950ce39a193b72027c22de9'
PROFILES = ['qa_no_rag_fp16', 'm3_text_fp16', 'integrated_fp16', 'integrated_nf4', 'integrated_no_tool_fp16']


def plan(root):
    root = Path(root)
    receipt = receive_closure(root)
    if not receipt['judge_review']['judge_validated_for_task_after_technical_gates']:
        raise ValueError('Human judge closure required')
    files = read_archive(root/'final/evidence/comparison_02/original_results.zip', COMPARISON_SHA)
    jobs = []
    expected_ids = None
    for profile in PROFILES:
        rows = [json.loads(s) for s in files[profile+'/predictions.jsonl'].decode().splitlines()]
        ids = [r['id'] for r in rows]
        if len(ids) != 22 or len(set(ids)) != 22:
            raise ValueError('Each profile must retain all 22 cases')
        if expected_ids is None:
            expected_ids = set(ids)
        elif set(ids) != expected_ids:
            raise ValueError('Profiles have differing case IDs')
        for row in rows:
            payload = evidence_payload(row['record'])
            if set(payload) != {'pregunta', 'respuesta_propuesta', 'fragmentos', 'calculos_verificables'}:
                raise ValueError('Unexpected judge payload fields')
            jobs.append({'profile': profile, 'id': row['id'], 'source_record_sha256': canonical_hash(row),
                         'judge_payload': payload, 'payload_sha256': canonical_hash(payload),
                         'judgement': None, 'dispatch_status': 'not_authorized_budget_pending'})
    return {
        'version': 'product-judge-plan-1', 'source_comparison_sha256': COMPARISON_SHA,
        'judge_human_closure_sha256': receipt['judge_review_sha256'],
        'jobs': jobs, 'profiles': PROFILES, 'cases_per_profile': 22, 'total_cases': len(jobs),
        'gold_in_judge_payload': False, 'system_outputs_regenerated': False,
        'network_requests_made': 0, 'paid_dispatch_authorized': False,
        'current_authorized_total_usd': '5.00',
        'estimated_or_reserved_total_usd': '4.1974125',
        'local_margin_usd': str(Decimal(5)-Decimal('4.1974125')),
        'decision_required': 'Keep USD 5 and reconcile verifiable billing, or obtain an explicit new TOTAL ceiling. Never reset unknown reservations.',
        'completeness_policy': 'Keep 110 rows, including invalid structured outputs. No favourable subset, inferred LLM score, or partial-as-complete scorecard.',
        'domain_policy': 'Raw LLM scores do not replace signed semantic/critical checks; domain stays pending where any requirement is missing.',
    }


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Do not overwrite an existing evaluation plan')
    args.output.write_text(json.dumps(plan(Path(__file__).resolve().parents[1]), ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(args.output)
