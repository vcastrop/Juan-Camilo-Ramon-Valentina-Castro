"""Same validated judge, new saved product inputs, explicitly authorized total USD 7."""
from datetime import datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
import time

from final.api_budget7 import BudgetLedger7, AUTHORIZATION
from final.confirmation13_receipt import SHA13
from final.gemini_judge_client import ApiFailure
from final.human_closure_receipt import receive_closure
from final.hydrogen_confirmation13 import verify_checkpoint as previous_checkpoint, check_drive as previous_drive
from final.hydrogen_judge_client import validate_config
from final.hydrogen_paid12 import PaidGenerator, POLICY as GENERATION_POLICY
from final.paid_transition_preflight import read_archive
from final.prepare_eval_final import canonical_hash
from final.prepare_product_judge_plan import plan

POLICY = {**GENERATION_POLICY, 'version': 'product-judge-14', 'total_authorized_usd': '7.00',
          'authorization_version': AUTHORIZATION['version'], 'product_cases': 110,
          'outputs_regenerated': False, 'calibration_regenerated': False,
          'gold_in_judge_payload': False, 'automatic_transport_retries': 0}


def checkpoint(root):
    root = Path(root)
    closure = receive_closure(root)
    if not closure['judge_review']['judge_validated_for_task_after_technical_gates']:
        raise ValueError('Human judge closure not complete')
    result = previous_checkpoint(root)
    files = read_archive(root/'final/evidence/confirmation_13/original_results.zip', SHA13)
    result['metadata'] = json.loads(files['metadata.json'])
    result['budget_snapshot'] = json.loads(files['budget_ledger_snapshot.json'])
    result['base_drive']['budget_snapshot'] = result['budget_snapshot']
    result['financial_checkpoint_archive_sha256'] = SHA13
    return result


def check_drive(folder, cfg, saved):
    # Before migration, require every original marker and the complete 57-entry ledger.
    previous_drive(folder, cfg, saved)
    path = Path(folder)/'hydrogen_confirmation_13.started.json'
    from final.hydrogen_confirmation13 import POLICY as CONFIRMATION_POLICY
    if not path.is_file():
        raise ApiFailure('confirmation13_marker_required')
    marker = json.loads(path.read_text(encoding='utf-8'))
    if marker.get('policy') != CONFIRMATION_POLICY or marker.get('generation_config_sha256') != canonical_hash(cfg):
        raise ApiFailure('confirmation13_marker_changed')
    if marker.get('calibration_archive_sha256') != 'b69d2741286ae85c2400d9412599337f6ab66dbdb516fbd1b5b3186f9b73ec45':
        raise ApiFailure('confirmation13_provenance_changed')


def register(folder, cfg, saved):
    check_drive(folder, cfg, saved)
    path = Path(folder)/'product_judge_14.started.json'
    with path.open('x', encoding='utf-8') as stream:
        json.dump({'started_utc': datetime.now(timezone.utc).isoformat(), 'policy': POLICY,
                   'generation_config_sha256': canonical_hash(cfg), 'checkpoint_sha256': SHA13}, stream, indent=2)


def product_plan(root):
    result = plan(root)
    result.update(version='product-paid14-plan', current_authorized_total_usd='7.00',
                  local_margin_usd='2.8025875', authorization=AUTHORIZATION,
                  user_budget_authorized=True, runtime_checks_complete=False,
                  decision_required='Runtime confirmation, history/marker verification and migration before dispatch')
    for job in result['jobs']:
        job['dispatch_status'] = 'pending_runtime_checks'
    return result


def record_from_payload(payload):
    from m3.judge import evidence_payload
    record = {'question': payload['pregunta'], 'output': payload['respuesta_propuesta'],
              'contexts': payload['fragmentos'],
              'tool_trace': [{'tool_result': {'ok': True, **c}} for c in payload['calculos_verificables']]}
    if evidence_payload(record) != payload:
        raise ValueError('Payload round trip changed judge evidence')
    return record


class ProductGenerator(PaidGenerator):
    def __init__(self, key, cfg, ledger_path, audit_path, *, checkpoint,
                 confirmed_paid_project=False, confirmed_total_usd7=False, exclusive_project_use=False,
                 transport=None, clock=time.monotonic, sleeper=time.sleep, now_utc=None):
        validate_config(cfg)
        if not (confirmed_paid_project and confirmed_total_usd7 and exclusive_project_use):
            raise ApiFailure('paid_exclusive_use_and_usd7_total_confirmation_required')
        if not isinstance(key, str) or not key.strip():
            raise ApiFailure('missing_api_key')
        if (now_utc or datetime.now(timezone.utc)).date().isoformat() > POLICY['price_recheck_after_utc']:
            raise ApiFailure('price_recheck_required')
        self.ledger = BudgetLedger7(ledger_path)
        self.ledger.used_or_reserved()
        marker = json.loads((Path(ledger_path).parent/'product_judge_14.started.json').read_text(encoding='utf-8'))
        if marker.get('policy') != POLICY or marker.get('checkpoint_sha256') != SHA13:
            raise ApiFailure('product14_marker_changed')
        self._key = key
        self.cfg = dict(cfg, billing_mode=POLICY['billing_mode'], total_authorized_usd='7.00',
                        calibration_estimate_limit_usd='7.00', request_timeout_seconds=180,
                        price_snapshot_utc=POLICY['price_snapshot_utc'])
        self.audit_path = Path(audit_path)
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        self.stage_start = Decimal(0)
        self.clock, self.sleeper = clock, sleeper
        self.transport = transport or self._request
        self.last_dispatch, self.model_info = None, None
        self.actual_version = checkpoint['metadata']['actual_model_version']
        self.request_seed, self.last_generation = cfg['seed'], {}
        self.generation_calls, self.retry_count = 0, 0
        self.last_error, self.provider_failure = None, None
        self.observed_response_count = 0
        self.checkpoint = checkpoint

    def journal(self, entry):
        if entry.get('event') == 'generation_response':
            self.observed_response_count += 1
        super().journal({**entry, 'protocol': POLICY['version'], 'authorized_total_usd': '7.00'})

    def generate(self, system, user):
        try:
            return super().generate(system, user)
        except ApiFailure:
            raise
        except (RuntimeError, ValueError, OSError) as exc:
            self.last_error = {'code': 'local_budget_or_io_guard_stopped', 'exception_type': type(exc).__name__}
            raise ApiFailure('local_budget_or_io_guard_stopped') from None
