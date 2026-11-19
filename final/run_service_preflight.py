"""Real Colab T4 deployment preflight. No judge, paid calls or score replacement."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('USE_TF', '0')
os.environ.setdefault('ANONYMIZED_TELEMETRY', 'false')
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')


def run(candidate, output):
    from final.service_environment import inspect_environment
    output = Path(output)
    if output.exists() and any(output.iterdir()): raise ValueError('Use a new empty output directory')
    output.mkdir(parents=True, exist_ok=True)
    meta = {'status': 'started', 'python': sys.version,
            'purpose': 'real_models_preflight_not_semantic_benchmark_or_ZeroGPU_validation'}
    try:
        report = inspect_environment()
        meta.update(environment=report, packages=report['packages'])
        if not report['ready']: raise RuntimeError('software_environment_not_ready')
        return _run(candidate, output, meta)
    except Exception as exc:
        meta.update(status='failed_partial_evidence_retained', error_type=type(exc).__name__)
        raise
    finally:
        (output/'metadata.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')


def _run(candidate, output, meta):
    from final.space_payload import unpack
    archive = Path(candidate)/'runtime_payload.zip'
    sha = hashlib.sha256(archive.read_bytes()).hexdigest()
    generated_app = (Path(candidate)/'app.py').read_text(encoding='utf-8')
    if "PAYLOAD_SHA = '"+sha+"'" not in generated_app:
        raise ValueError('Generated app and payload differ')
    runtime = Path(tempfile.mkdtemp(prefix='contractrisk_preflight_payload_'))
    manifest = unpack(archive, sha, runtime)
    # Inference imports are exclusively from the verified payload, not checkout.
    for name in list(sys.modules):
        if name == 'final' or name.startswith('final.'):
            del sys.modules[name]
    sys.path[:0] = [str(runtime), str(runtime/'m3')]
    from final.service_contract import Service
    from final.service_runtime import load_runtime, verify_assets
    from PIL import Image, ImageDraw, ImageFont
    import torch
    if not torch.cuda.is_available() or 'T4' not in torch.cuda.get_device_name(0):
        raise RuntimeError('Select Colab T4')
    meta.update(source_commit=manifest['source_commit'], payload_sha256=sha,
                gpu=torch.cuda.get_device_name(0))
    started = time.perf_counter()
    try:
        service = Service(load_runtime(), manifest['source_commit'])
        meta['load_seconds'] = time.perf_counter()-started
        health = service.health()
        (output/'health.json').write_text(json.dumps(health, indent=2), encoding='utf-8')
        if not health['contract_system_ready']: raise RuntimeError('Readiness check failed')
        docs = verify_assets(runtime)
        identity = docs[0]['doc_id']
        # Synthetic rendering of an actual public source, not a real signed contract.
        font_path = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
        if not font_path.is_file(): raise RuntimeError('Install fonts-dejavu-core')
        import textwrap
        text = '\n'.join(textwrap.fill(line, width=72) for line in docs[0]['text'].splitlines())
        font = ImageFont.truetype(str(font_path), 23)
        image = Image.new('RGB', (1100, max(400, 60+len(text.splitlines())*31)), 'white')
        ImageDraw.Draw(image).multiline_text((20, 20), text, font=font, fill='black', spacing=8)
        image.save(output/'synthetic_public_fixture.png')
        cases = [
            ('qa_source', '¿Cuál es la entidad del contrato '+identity+'?', 'qa', '', None, True),
            ('m1_description', '', 'sufficiency', 'Prestación de servicios de mantenimiento preventivo de equipos de cómputo durante doce meses, con visitas mensuales y soporte técnico.', None, True),
            ('visual_source', '¿Cuál es la entidad visible en esta ficha?', 'qa', '', image, True),
            ('numeric_source', '¿Cuál es la diferencia entre los valores de los contratos '+identity+' y '+docs[1]['doc_id']+'?', 'qa', '', None, True),
            ('missing_source', '¿Qué concluye el informe de auditoría del contrato '+identity+'?', 'qa', '', None, True),
            ('blank_image', '¿Cuál es el valor visible?', 'qa', '', Image.new('RGB', (600, 400), 'white'), True),
            ('invalid_input', '', 'qa', '', None, True),
        ]
        rows = []
        for name, question, mode, description, picture, consent in cases:
            display, event = service.compute(question, mode, description, picture, consent)
            service.observe_finished(event)
            row = {'case': name, 'display': display, 'event': event}
            rows.append(row)
            with (output/'requests.jsonl').open('a', encoding='utf-8') as f:
                f.write(json.dumps(row, ensure_ascii=False)+'\n')
            print(json.dumps(row, ensure_ascii=False), flush=True)
        meta['technical_errors'] = [r['case'] for r in rows if not r['event']['success'] and r['case'] != 'invalid_input']
        meta['status'] = 'completed_requires_review' if not meta['technical_errors'] else 'completed_with_technical_errors'
        meta['post_health'] = service.health()
        indexed = {r['case']: r for r in rows}
        meta['observations_not_quality_scores'] = {
            'm1_classifier_used': indexed['m1_description']['event']['classifier_used'],
            'visual_pipeline_used': indexed['visual_source']['event']['vision_used'],
            'tool_success': indexed['numeric_source']['event']['tool_used'],
            'missing_source_abstention': indexed['missing_source']['event']['abstention'],
            'blank_image_abstention': indexed['blank_image']['event']['abstention'],
            'invalid_input_rejected': indexed['invalid_input']['event']['error_code'] == 'invalid_input'}
        meta['semantic_quality_approved'] = False
    except Exception as exc:
        meta['status'], meta['error_type'] = 'failed_partial_evidence_retained', type(exc).__name__
        raise
    finally:
        (output/'metadata.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    return meta


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(run(args.candidate, args.output), indent=2))
