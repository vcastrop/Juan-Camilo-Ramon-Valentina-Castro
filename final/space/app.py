"""Infrastructure smoke only; no simulated contractual answers."""
import spaces  # Must precede libraries that may initialize CUDA.
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import telemetry
from fastapi.responses import JSONResponse
from starlette.routing import Route
import gradio as gr


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
    started = time.perf_counter()
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError('GPU unavailable')
    value = (torch.ones(1, device='cuda') + 1).item()
    return {'device': torch.cuda.get_device_name(0), 'tensor_check': value == 2,
            'latency_seconds': time.perf_counter()-started}


def gpu_probe(output):
    # Runs on CPU after the GPU callback, without holding a GPU for W&B I/O.
    success = bool(output.get('tensor_check', False))
    payload = telemetry.event('gpu_smoke', output['latency_seconds'], success, gpu=True)
    return {'result': output, 'wandb_status': telemetry.send(payload),
            'models_loaded': False}


def healthz(request):
    return JSONResponse(health_payload())


def readyz(request):
    return JSONResponse(status_code=503, content=health_payload())


with gr.Blocks(title='ContractRisk Colombia') as demo:
    gr.Markdown('# ContractRisk Colombia\n\n'
                '**Prueba inicial de infraestructura.** El sistema contractual todavía '
                'no está integrado. Esta versión no evalúa contratos ni recibe imágenes.\n\n'
                'La decisión contractual corresponde a una persona; no se determina fraude.')
    gr.Button('Consultar estado sin usar GPU').click(health_payload, outputs=gr.JSON())
    gr.Button('Registrar prueba técnica').click(infrastructure_probe, outputs=gr.JSON())
    gr.Markdown('La prueba siguiente consume cuota de ZeroGPU. No carga modelos.')
    gpu_result = gr.JSON()
    gr.Button('Probar asignación GPU').click(
        gpu_operation, outputs=gpu_result,
    ).success(gpu_probe, inputs=gpu_result, outputs=gpu_result)

HEALTH_ROUTES = [Route('/healthz', healthz), Route('/readyz', readyz)]


def launch(server_port=7860, prevent_thread_lock=False):
    # One server, started via Gradio so ZeroGPU can register its handlers.
    return demo.queue(max_size=4).launch(
        server_name='0.0.0.0', server_port=server_port,
        prevent_thread_lock=prevent_thread_lock, ssr_mode=False,
        app_kwargs={'routes': HEALTH_ROUTES},
    )

if __name__ == '__main__':
    launch()
