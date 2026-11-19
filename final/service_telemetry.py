"""Structured public-service metadata only; no stdout/code/query capture by W&B."""
import json
import os
import threading

from final.service_contract import validate_event


class Telemetry:
    def __init__(self):
        self.run, self.lock = None, threading.Lock()
        self.status = 'not_tested' if os.getenv('WANDB_API_KEY') else 'disabled'

    def send(self, payload):
        validate_event(payload)
        print(json.dumps(payload, ensure_ascii=False), flush=True)
        if not os.getenv('WANDB_API_KEY'):
            self.status = 'disabled'
            return self.status
        with self.lock:
            try:
                import wandb
                if self.run is None:
                    self.run = wandb.init(entity=os.getenv('WANDB_ENTITY', 'jcramonp-eanit'),
                        project=os.getenv('WANDB_PROJECT', 'contractrisk-final'), job_type='public-contract-service',
                        config={'phase': 'contractual_candidate', 'version': payload['version']},
                        settings=wandb.Settings(console='off', disable_git=True, disable_code=True,
                            disable_job_creation=True, x_disable_stats=True, init_timeout=20))
                values = {'request/success': int(payload['success'])}
                if payload['error_code'] != 'gpu_dispatch_error':
                    values['request/latency_seconds'] = payload['latency_seconds']
                for flag in ['rag_used', 'tool_used', 'vision_used', 'classifier_used', 'router_used', 'abstention']:
                    if payload[flag] is not None: values['usage/'+flag] = int(payload[flag])
                self.run.log(values)
                self.status = 'queued_check_dashboard'
            except Exception:
                self.status = 'error_check_permissions_or_service'
        return self.status
