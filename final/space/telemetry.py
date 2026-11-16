"""Allow-listed technical events only; never accepts user query/image content."""
from datetime import datetime, timezone
import json
import os
import sys
import threading
import uuid

_lock = threading.Lock()
_run = None
_status = 'disabled' if not os.getenv('WANDB_API_KEY') else 'not_tested'


def status():
    return _status


def event(kind, latency_seconds, success, gpu=False):
    if kind not in {'infrastructure_smoke', 'gpu_smoke'}:
        raise ValueError('Unsupported event kind')
    seconds = float(latency_seconds)
    if not 0 <= seconds < 3600:
        raise ValueError('Invalid latency')
    payload = {
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'request_id': str(uuid.uuid4()),
        'event_type': kind,
        'latency_seconds': seconds,
        'success': bool(success),
        'rag_used': False, 'tool_used': False, 'vision_used': False,
        'gpu_probe_used': bool(gpu), 'abstention': None,
        'phase': 'infrastructure_only',
        'version': os.getenv('CONTRACTRISK_VERSION', 'unrecorded')[:80],
    }
    print(json.dumps(payload, ensure_ascii=False), file=sys.stdout, flush=True)
    return payload


def send(payload):
    """Send sanitized aggregates only, no console/code/environment upload."""
    global _run, _status
    if not os.getenv('WANDB_API_KEY'):
        _status = 'disabled'
        return _status
    with _lock:
        try:
            import wandb
            if _run is None:
                _run = wandb.init(
                    entity=os.getenv('WANDB_ENTITY', 'jcramonp-eanit'),
                    project=os.getenv('WANDB_PROJECT', 'contractrisk-final'),
                    job_type='infrastructure_smoke',
                    config={'phase': 'infrastructure_only'},
                    settings=wandb.Settings(console='off', disable_git=True,
                                            disable_code=True, disable_job_creation=True,
                                            x_disable_stats=True, init_timeout=20),
                )
            _run.log({
                'request/latency_seconds': payload['latency_seconds'],
                'usage/infrastructure_probe': 1,
                'usage/gpu_probe': int(payload['gpu_probe_used']),
                'request/success': int(payload['success']),
            })
            # log() queues delivery; do not label this as confirmed remote sync.
            _status = 'queued_check_dashboard'
        except Exception:
            _status = 'error_check_permissions_or_service'
    return _status
