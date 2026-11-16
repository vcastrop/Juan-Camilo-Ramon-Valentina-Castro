"""Infrastructure smoke only; no simulated contractual answers."""
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import telemetry
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import gradio as gr
import spaces


def health_payload():
    return {
        'status': 'alive', 'phase': 'infrastructure_only',
        'contract_system_ready': False, 'models_loaded': False,
        'index_ready': False, 'wandb_status': telemetry.status(),
    }


def infrastructure_probe():
    started = time.perf_counter()
    payload = telemetry.event('infrastructure_smoke', time.perf_counter()-started, True)
    return {'event': payload, 'wandb_status': telemetry.send(payload),
            'note': 'Prueba técnica; no es una consulta ni una evaluación del modelo.'}


@spaces.GPU(duration=20)
def gpu_operation():
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError('GPU unavailable')
    value = (torch.ones(1, device='cuda') + 1).item()
    return {'device': torch.cuda.get_device_name(0), 'tensor_check': value == 2}


def gpu_probe():
    started = time.perf_counter()
    try:
        output = gpu_operation()
        success = bool(output['tensor_check'])
    except Exception:
        output = {'error': 'GPU no verificada; revisar cuota y configuración del Space.'}
        success = False
    payload = telemetry.event('gpu_smoke', time.perf_counter()-started, success, gpu=True)
    return {'result': output, 'wandb_status': telemetry.send(payload),
            'models_loaded': False}


api = FastAPI(title='ContractRisk infrastructure')


@api.get('/healthz')
def healthz():
    return health_payload()


@api.get('/readyz')
def readyz():
    return JSONResponse(status_code=503, content=health_payload())


with gr.Blocks(title='ContractRisk Colombia') as demo:
    gr.Markdown('# ContractRisk Colombia\n\n'
                '**Prueba inicial de infraestructura.** El sistema contractual todavía '
                'no está integrado. Esta versión no evalúa contratos ni recibe imágenes.\n\n'
                'La decisión contractual corresponde a una persona; no se determina fraude.')
    gr.Button('Consultar estado sin usar GPU').click(health_payload, outputs=gr.JSON())
    gr.Button('Registrar prueba técnica').click(infrastructure_probe, outputs=gr.JSON())
    gr.Markdown('La prueba siguiente consume cuota de ZeroGPU. No carga modelos.')
    gr.Button('Probar asignación GPU').click(gpu_probe, outputs=gr.JSON())

app = gr.mount_gradio_app(api, demo.queue(max_size=4), path='/')

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=7860, log_level='warning', access_log=False)
