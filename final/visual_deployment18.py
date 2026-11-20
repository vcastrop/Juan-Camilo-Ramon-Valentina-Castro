"""Frozen post-hoc OCR diagnostic. No model/prompt change, no retries or judge API."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import textwrap
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'m3')]
ARCHIVE_SHA = '7a9146dfa7a3fc6eccf36a727438d7f2a9c5ee4f3ad4723c8b23170fc8c1c72d'
PROTOCOL = ROOT/'final/evidence/visual18_protocol'
IDS = ['full_original_once', 'compact_plain_a', 'compact_grouped_a',
       'compact_plain_b', 'compact_grouped_b', 'altered_amount', 'missing_amount', 'blank']


def sha(data): return hashlib.sha256(data).hexdigest()


def prepare(output, font_path):
    """Generate and commit inputs BEFORE GPU execution, never after seeing results."""
    from PIL import Image, ImageDraw, ImageFont
    from final.service_runtime import verify_assets
    docs = verify_assets()
    original = ROOT/'final/evidence/deployment17_completed/original_results.zip'
    if sha(original.read_bytes()) != ARCHIVE_SHA: raise ValueError('Changed source evidence')
    output = Path(output)
    if output.exists(): raise ValueError('Do not replace a frozen protocol')
    output.mkdir(parents=True)
    with zipfile.ZipFile(original) as z:
        baseline = z.read('deployment17_results/synthetic_public_fixture.png')
        import io
        payload = zipfile.ZipFile(io.BytesIO(z.read('deployment17_candidate/runtime_payload.zip')))
        source_manifest = json.loads(payload.read('manifest.json'))
    font = ImageFont.truetype(str(font_path), 30)
    cases = []
    for i, identity in enumerate(IDS):
        doc = docs[1] if identity.endswith('_b') else docs[0]
        lines = doc['text'].splitlines()
        value = next(s.split(':', 1)[1].strip() for s in lines if s.startswith('Valor del contrato (COP):'))
        modality = next(s.split(':', 1)[1].strip() for s in lines if s.startswith('Modalidad de contratación:'))
        expected = {'id_contrato': doc['doc_id'], 'valor_cop': value, 'modalidad': modality}
        control = None
        path = output/(identity+'.png')
        if identity == 'full_original_once':
            path.write_bytes(baseline)
        elif identity == 'blank':
            expected, control = None, 'unreadable'
            Image.new('RGB', (1200, 500), 'white').save(path)
        else:
            selected = [s for s in lines if s.startswith(('Identificador del contrato:', 'Entidad:',
                        'Objeto registrado:', 'Modalidad de contratación:', 'Valor del contrato (COP):'))]
            if 'grouped' in identity:
                rendered_value = f'{int(value):,}'.replace(',', '.')+' COP'
                selected = [s if not s.startswith('Valor del contrato (COP):') else 'Valor del contrato (COP): '+rendered_value for s in selected]
            if identity == 'altered_amount':
                expected['valor_cop'] = str(int(value)+1_000_000)
                control = 'visual_source_conflict'
                selected = [s if not s.startswith('Valor del contrato (COP):') else 'Valor del contrato (COP): '+expected['valor_cop'] for s in selected]
            if identity == 'missing_amount':
                expected['valor_cop'], control = None, 'missing_visual_fields'
                selected = [s for s in selected if not s.startswith('Valor del contrato (COP):')]
            text = '\n\n'.join(textwrap.fill(s, width=60) for s in [
                'FICHA SINTETICA DE PRUEBA. NO ES DOCUMENTO FIRMADO.', *selected])
            image = Image.new('RGB', (1200, 70+len(text.splitlines())*44), 'white')
            ImageDraw.Draw(image).multiline_text((25, 20), text, font=font, fill='black', spacing=10)
            image.save(path)
        cases.append({'id': identity, 'file': path.name, 'image_sha256': sha(path.read_bytes()),
                      'question': '¿Qué modalidad y valor del contrato aparecen en la imagen?',
                      'expected_for_diagnostics_only': expected, 'expected_guard': control,
                      'origin': 'synthetic_source_render_not_real_document',
                      'is_control': control is not None})
    protocol = {'version': 'visual-deployment-diagnostic-18', 'post_hoc': True,
                'reason': 'Investigate extra OCR zero observed in deployment17; not blind or representative.',
                'baseline_archive_sha256': ARCHIVE_SHA, 'baseline_source_commit': source_manifest['source_commit'],
                'source_hashes': {n:s for n,s in source_manifest['files'].items() if n.endswith('.py')},
                'font_sha256': sha(Path(font_path).read_bytes()), 'cases': cases,
                'policy': {'one_pass': True, 'semantic_retries': 0, 'model_prompt_changes': False,
                           'prior_results_replaced': False, 'new_api_calls': 0,
                           'full_original_once': 'One explicit replication, never replaces the saved failing result.'}}
    (output/'protocol.json').write_text(json.dumps(protocol, ensure_ascii=False, indent=2), encoding='utf-8')
    return protocol


def load_protocol(folder=PROTOCOL):
    folder = Path(folder)
    protocol = json.loads((folder/'protocol.json').read_text(encoding='utf-8'))
    if [c['id'] for c in protocol['cases']] != IDS or protocol['policy']['semantic_retries'] != 0:
        raise ValueError('Frozen diagnostic agenda changed')
    for case in protocol['cases']:
        if Path(case['file']).name != case['file'] or sha((folder/case['file']).read_bytes()) != case['image_sha256']:
            raise ValueError('Frozen image changed')
    for name, digest in protocol['source_hashes'].items():
        if sha((ROOT/name).read_bytes().replace(b'\r\n', b'\n')) != digest:
            raise ValueError('Inference implementation differs from deployment17: '+name)
    return protocol


def diagnose(case, record):
    """Expected values enter only AFTER real inference; these are not human verdicts."""
    from final.integration import normalized
    from final.visual_fields import amount_literal
    visual = ((record.get('visual') or {}).get('output') or {})
    output = record.get('output') or {}
    expected = case['expected_for_diagnostics_only']
    fields = {key: visual.get(key) == value for key, value in (expected or {}).items()}
    exact = bool(expected) and all(fields.values())
    text = output.get('respuesta', '')
    amounts = [amount_literal(s) for s in re.findall(r'(?<!\w)\d(?:[\d.,]*\d)?(?!\w)', text)]
    check = bool(expected and expected['valor_cop'] is not None and expected['valor_cop'] in amounts
                 and normalized(expected['modalidad']) in normalized(text))
    abstention = output.get('abstencion') is True
    return {'visual_field_matches': fields, 'all_expected_visual_fields_exact': exact,
            'observed_guard': record.get('guard'), 'abstention': output.get('abstencion'),
            'expected_guard_exact': record.get('guard') == case['expected_guard'] if case['is_control'] else None,
            'control_protected': abstention if case['is_control'] else None,
            'answer_amount_and_modality_literal_check': check,
            'usable_legible_case_automatic_only': bool(not case['is_control'] and exact and check and not abstention and output.get('citas')),
            'ocr_error_blocked': bool(expected and not exact and abstention),
            'potential_unsafe_answer_requires_review': bool(not abstention and (case['is_control'] or not exact)),
            'human_semantic_approval': None}


def run(output):
    from PIL import Image
    from final.service_environment import require_environment
    from final.service_runtime import load_runtime
    from final.service_contract import event
    output = Path(output)
    if output.exists(): raise ValueError('Use a new directory; never replace prior outputs')
    output.mkdir(parents=True)
    meta = {'status': 'started', 'protocol_sha256': sha((PROTOCOL/'protocol.json').read_bytes()),
            'source_commit': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
            'purpose': 'post_hoc_frozen_visual_diagnostic_not_final_benchmark', 'api_calls': 0,
            'started_utc': datetime.now(timezone.utc).isoformat(), 'prior_results_replaced': False}
    rows = []
    try:
        protocol = load_protocol()
        meta['environment'] = require_environment()
        import torch
        if not torch.cuda.is_available() or 'T4' not in torch.cuda.get_device_name(0): raise RuntimeError('Select T4')
        meta['gpu'] = torch.cuda.get_device_name(0)
        runtime = load_runtime()
        meta['health_before'] = {'models': runtime.model_state(), 'index': runtime.index_probe()}
        for case in protocol['cases']:
            # Only question, pixels and ordinary corpus enter the unchanged runtime.
            with Image.open(PROTOCOL/case['file']) as image:
                record = runtime.predict(case['question'], image=image.convert('RGB'))
            row = {'id': case['id'], 'record': record, 'diagnostics': diagnose(case, record),
                   'event': event(meta['source_commit'], record['latency_seconds'], record=record)}
            rows.append(row)
            with (output/'responses.jsonl').open('a', encoding='utf-8') as f:
                f.write(json.dumps(row, ensure_ascii=False)+'\n')
            print(json.dumps(row, ensure_ascii=False), flush=True)
        meta.update(status='completed_requires_review', completed_cases=len(rows),
            usable_legible_cases_automatic_only=sum(r['diagnostics']['usable_legible_case_automatic_only'] for r in rows),
            legible_case_denominator=5, control_denominator=3,
            protected_controls=sum(r['diagnostics']['control_protected'] is True for r in rows),
            potential_unsafe_cases=[r['id'] for r in rows if r['diagnostics']['potential_unsafe_answer_requires_review']],
            deployment_quality_approved=False)
    except Exception as exc:
        meta.update(status='failed_partial_evidence_retained', completed_cases=len(rows), error_type=type(exc).__name__)
        raise
    finally:
        (output/'metadata.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    return meta


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('operation', choices=['prepare', 'run'])
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--font', type=Path)
    args = p.parse_args()
    result = prepare(args.output, args.font) if args.operation == 'prepare' else run(args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))
