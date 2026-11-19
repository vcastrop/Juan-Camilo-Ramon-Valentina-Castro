"""Build template: publish only the generated, checksum-bound version."""
import spaces  # Required before anything importing CUDA.
import os
os.environ.setdefault('USE_TF', '0')
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
os.environ.setdefault('ANONYMIZED_TELEMETRY', 'false')
os.environ.setdefault('GRADIO_ANALYTICS_ENABLED', 'false')
from pathlib import Path
import sys
import tempfile

PAYLOAD_SHA = '__PAYLOAD_SHA__'
SOURCE_COMMIT = '__SOURCE_COMMIT__'
# __BOOTSTRAP__
runtime_dir = Path(tempfile.mkdtemp(prefix='contractrisk_runtime_'))
manifest = unpack(Path(__file__).with_name('runtime_payload.zip'), PAYLOAD_SHA, runtime_dir)
if manifest['source_commit'] != SOURCE_COMMIT:
    raise ValueError('Unexpected code version')
sys.path[:0] = [str(runtime_dir), str(runtime_dir/'m3')]
from final.service_contract import Service, InputError, validate, event
from final.service_telemetry import Telemetry
from final.service_runtime import load_runtime
from fastapi.responses import JSONResponse
from starlette.routing import Route
import gradio as gr

service = Service(None, SOURCE_COMMIT, 'models_not_loaded')
telemetry = Telemetry()


@spaces.GPU(duration=120)
def compute(question, mode, description, image, consent):
    # Only model inference here; W&B/network work happens after GPU release.
    return service.compute(question, mode, description, image, consent)


try:
    service = Service(load_runtime(), SOURCE_COMMIT)
except Exception:
    # No private paths, provider exception bodies or tokens in logs/UI.
    print('ContractRisk startup_failed: models_or_index_not_ready', flush=True)
    service = Service(None, SOURCE_COMMIT, 'models_or_index_not_ready')


def precheck(question, mode, description, image, consent):
    try: validate(question, mode, description, image, consent)
    except InputError as exc:
        telemetry.send(event(SOURCE_COMMIT, 0, mode, error='invalid_input'))
        raise gr.Error(str(exc)) from None
    if not service.health()['contract_system_ready']:
        telemetry.send(event(SOURCE_COMMIT, 0, mode, error='not_ready'))
        raise gr.Error('Los modelos o el índice no están listos. Consulta el estado.')


def finish(payload):
    service.observe_finished(payload)
    return {'evento': payload, 'wandb_status': telemetry.send(payload)}


def dispatch_failure(mode):
    payload = event(SOURCE_COMMIT, 0, mode, error='gpu_dispatch_error')
    # Zero means no processing measurement, not zero end-to-end latency.
    return {'error': 'gpu_dispatch_error', 'message': 'No se completó la asignación o ejecución GPU.'}, finish(payload)


def state():
    return dict(service.health(), wandb_status=telemetry.status)


def healthz(request):
    return JSONResponse(state())


def readyz(request):
    data = state()
    return JSONResponse(data, status_code=200 if data['contract_system_ready'] else 503)


with gr.Blocks(title='ContractRisk Colombia', delete_cache=(3600, 3600)) as demo:
    gr.Markdown('# ContractRisk Colombia\n\nPrototipo académico — Built with Qwen. '
        'Solo investigación/evaluación no comercial. Consulta fichas públicas con fuentes; '
        'el modo M1 evalúa suficiencia descriptiva, **no fraude ni autenticidad**. '
        'Verifica cada resultado. El candidato FP16 conserva seis fallos de dominio en 22 entradas evaluadas.')
    mode = gr.Radio([('Consulta con fuentes (texto o captura)', 'qa'),
                     ('M1: suficiencia descriptiva', 'sufficiency')], value='qa', label='Modo')
    question = gr.Textbox(label='Pregunta (máximo 1200 caracteres)', max_lines=5)
    description = gr.Textbox(label='Descripción para M1 (máximo 8000 caracteres)', max_lines=8)
    image = gr.Image(type='pil', label='Captura opcional de ficha pública (10 MB / 12 MP)')
    consent = gr.Checkbox(label='Usaré solo información pública sin datos personales; entiendo que es experimental y que las imágenes pueden quedar temporalmente en caché.', value=False)
    submit = gr.Button('Consultar')
    result, record, tracking = gr.JSON(label='Resultado y fuentes'), gr.State(), gr.JSON(label='Registro técnico sin contenido de entrada')
    inputs = [question, mode, description, image, consent]
    checked = submit.click(precheck, inputs=inputs, outputs=None, queue=False)
    inference = checked.success(compute, inputs=inputs, outputs=[result, record], concurrency_limit=1)
    inference.success(finish, inputs=record, outputs=tracking, queue=False)
    inference.failure(dispatch_failure, inputs=mode, outputs=[result, tracking], queue=False)
    gr.Button('Consultar salud y disponibilidad (sin GPU)').click(state, outputs=gr.JSON(), queue=False)


def launch(server_port=7860, prevent_thread_lock=False):
    return demo.queue(max_size=4, default_concurrency_limit=1).launch(
        server_name='0.0.0.0', server_port=server_port, ssr_mode=False,
        prevent_thread_lock=prevent_thread_lock, max_file_size='10mb',
        show_error=False, enable_monitoring=False,
        blocked_paths=[str(runtime_dir), '/proc', '/home/user/.cache'],
        app_kwargs={'routes': [Route('/healthz', healthz), Route('/readyz', readyz)]})


if __name__ == '__main__':
    launch()
