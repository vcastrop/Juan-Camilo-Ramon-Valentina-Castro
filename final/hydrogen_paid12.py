"""Explicit paid continuation; frozen generation, cumulative accounting, no retries."""
from datetime import datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
import time

from final.api_budget import BudgetLedger
from final.gemini_judge_client import ApiFailure
from final.hydrogen_judge_client import HydrogenRESTGenerator, validate_config
from final.hydrogen_recovery11 import (
    RecoveryGenerator, check_current_drive, verify_checkpoint as verify10, POLICY as POLICY11,
)
from final.paid_transition_preflight import read_archive, transition_report, FIRST_SHA, BLOCKED_SHA
from final.prepare_eval_final import canonical_hash

POLICY = {
    'version': 'hydrogen-paid-12', 'billing_mode': 'paid_prepay_user_confirmed',
    'total_authorized_usd': '5.00', 'automatic_transport_retries': 0,
    'generation_payload_changed': False, 'request_timeout_seconds': 180,
    'price_snapshot_utc': '2026-11-19', 'price_recheck_after_utc': '2026-11-20',
    'input_price_per_million_usd': '1.50', 'output_price_per_million_usd': '7.50',
    'price_source': 'https://aistudio.google.com/docs/pricing#gemini-4-hydrogen',
    'actual_invoice_verified': False, 'unknown_reservations_released': False,
    'monthly_spend_cap_verified': False,
}


def verify_checkpoint(root):
    root = Path(root)
    checkpoint = verify10(root)
    first = read_archive(root/'final/evidence/hydrogen_11/original_results.zip', FIRST_SHA)
    blocked = read_archive(root/'final/evidence/hydrogen_11_billing_rerun/original_results.zip', BLOCKED_SHA)
    transition_report(first, blocked, checkpoint['budget_snapshot'])
    meta = json.loads(first['metadata.json'])
    rows = [json.loads(line) for line in first['raw_judgements.jsonl'].decode().splitlines()]
    valid = [row for row in rows if row['judgement']['score'] is not None]
    if len(valid) != 1 or valid[0]['judgement'] != checkpoint['saved_rows'][0]['judgement']:
        raise ValueError('Do not discard or regenerate valid notes')
    checkpoint['metadata'] = meta
    checkpoint['budget_snapshot'] = json.loads(first['budget_ledger_snapshot.json'])
    checkpoint['base_drive']['budget_snapshot'] = checkpoint['budget_snapshot']
    checkpoint['financial_checkpoint_archive_sha256'] = FIRST_SHA
    return checkpoint


def check_drive(folder, cfg, checkpoint):
    check_current_drive(folder, cfg, checkpoint)
    path = Path(folder)/'hydrogen_calibration_resume_2.started.json'
    if not path.is_file():
        raise ApiFailure('recovery11_marker_required')
    marker = json.loads(path.read_text(encoding='utf-8'))
    if (marker.get('config_sha256') != canonical_hash(cfg)
            or marker.get('policy') != POLICY11
            or marker.get('financial_checkpoint_archive_sha256') != '4e8d9f311ba4fdf83235cae8e69ba851b9161d5853e7613ddc657ce8039b9494'):
        raise ApiFailure('recovery11_marker_changed')


def register_paid(folder, cfg, checkpoint):
    check_drive(folder, cfg, checkpoint)
    with (Path(folder)/'hydrogen_paid_12.started.json').open('x', encoding='utf-8') as stream:
        json.dump({'started_utc': datetime.now(timezone.utc).isoformat(),
                   'policy': POLICY, 'generation_config_sha256': canonical_hash(cfg),
                   'financial_checkpoint_archive_sha256': FIRST_SHA,
                   'note': 'Paid status changes, not rubric, seeds, payload or saved valid notes'}, stream, indent=2)


class PaidGenerator(RecoveryGenerator):
    def __init__(self, key, cfg, ledger_path, audit_path, *, checkpoint,
                 confirmed_paid_project=False, exclusive_project_use=False,
                 transport=None, clock=time.monotonic, sleeper=time.sleep, now_utc=None):
        # Do not invoke the historical free-tier constructor or falsely attest free use.
        validate_config(cfg)
        if not confirmed_paid_project or not exclusive_project_use:
            raise ApiFailure('paid_project_and_exclusive_budget_confirmation_required')
        if not isinstance(key, str) or not key.strip():
            raise ApiFailure('missing_api_key')
        if (now_utc or datetime.now(timezone.utc)).date().isoformat() > POLICY['price_recheck_after_utc']:
            raise ApiFailure('price_recheck_required')
        check_drive(Path(ledger_path).parent, cfg, checkpoint)
        self._key = key
        self.cfg = dict(cfg)
        self.cfg.update(billing_mode=POLICY['billing_mode'], calibration_estimate_limit_usd='5.00',
                        request_timeout_seconds=180, price_snapshot_utc=POLICY['price_snapshot_utc'])
        self.ledger = BudgetLedger(ledger_path)
        self.audit_path = Path(audit_path)
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        self.stage_start = Decimal(0)
        self.clock = clock
        self.sleeper = sleeper
        self.transport = transport or self._request
        self.last_dispatch = None
        self.model_info = None
        self.actual_version = checkpoint['metadata']['actual_model_version']
        self.request_seed = cfg['seed']
        self.last_generation = {}
        self.generation_calls = 0
        self.last_error = None
        self.checkpoint = checkpoint
        self.retry_count = 0
        self.provider_failure = None

    def journal(self, entry):
        entry = dict(entry)
        if 'free_project_attested' in entry:
            entry['free_project_attested'] = False
        entry['billing_mode'] = POLICY['billing_mode']
        super().journal(entry)

    def generate(self, system, user):
        # No RecoveryGenerator retry loop. A single 503/timeout stops this run.
        try:
            result = HydrogenRESTGenerator.generate(self, system, user)
        except ApiFailure as exc:
            self.last_error = {'code': exc.code, 'http_status': exc.status,
                               **(self.provider_failure or {})}
            raise
        finally:
            if self.last_generation:
                self.last_generation.update(free_project_attested=False, billing_mode=POLICY['billing_mode'])
        return result
