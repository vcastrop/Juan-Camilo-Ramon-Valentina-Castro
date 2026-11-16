"""Development integration only; saves failures and never reads final QA gold."""
import argparse
from datetime import datetime, timezone
import gc
import hashlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import platform
import random
import subprocess
import sys
import textwrap
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'m3')]
from final.config import MODELS, SEED, VERSION


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture_font_path():
    """Use the packaged Unicode font, not an assumed OS installation."""
    spec = importlib.util.find_spec('matplotlib')
    if spec is not None and spec.origin:
        path = Path(spec.origin).parent/'mpl-data/fonts/ttf/DejaVuSans.ttf'
        if path.is_file():
            return path
    raise RuntimeError('Install final/requirements-integration.txt: packaged DejaVu font missing')


def create_fixtures(documents, folder):
    """Rasterized snapshot representations, not screenshots or legal documents."""
    from PIL import Image, ImageDraw, ImageFont, ImageEnhance
    folder.mkdir()
    font_path = fixture_font_path()
    font = ImageFont.truetype(str(font_path), 24)
    fixtures = []
    for i, doc_id in enumerate(['CO1.PCCNTR.1180445', 'CO1.PCCNTR.3156756'], 1):
        doc = next(d for d in documents if d['doc_id'] == doc_id)
        lines = [line for line in doc['text'].splitlines() if line.startswith(
            ('Identificador del contrato:', 'Entidad:', 'Objeto registrado:',
             'Modalidad de contratación:', 'Valor del contrato (COP):'))]
        rendered = ['FICHA DE PRUEBA REPRESENTADA DESDE EL SNAPSHOT', 'No es una captura real ni documento firmado.', '']
        for line in lines:
            rendered.extend(textwrap.wrap(line, width=67))
            rendered.append('')
        image = Image.new('RGB', (1120, max(500, len(rendered)*34+50)), 'white')
        draw = ImageDraw.Draw(image)
        draw.multiline_text((25, 20), '\n'.join(rendered), font=font, fill='black', spacing=10)
        path = folder/f'visual_dev_{i}.png'
        image.save(path)
        fixtures.append({'id': f'visual_dev_{i}', 'path': str(path), 'source_id': doc_id,
                         'question': '¿Qué modalidad y valor aparecen en la ficha de la imagen?',
                         'source_lines_for_human_review': lines, 'font': font.getname(),
                         'font_sha256': sha(font_path),
                         'origin': 'rendered_public_snapshot_not_real_screenshot'})
        if i == 1:
            changed = folder/'visual_dev_1_contrast.png'
            ImageEnhance.Contrast(image).enhance(0.85).save(changed)
            fixtures.append({'id': 'visual_dev_1_contrast', 'path': str(changed), 'source_id': doc_id,
                             'question': fixtures[0]['question'], 'pair_with': 'visual_dev_1',
                             'origin': 'development_invariance_contrast_0.85'})
    blank = folder/'visual_blank.png'
    Image.new('RGB', (1120, 500), 'white').save(blank)
    fixtures.append({'id': 'visual_blank', 'path': str(blank),
                     'question': '¿Qué valor del contrato aparece en esta imagen?', 'origin': 'synthetic_blank_direction_test'})
    return fixtures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Use a new output directory; existing evidence is never overwritten')
    args.output.mkdir(parents=True)
    meta = {'status': 'started', 'purpose': 'development_integration_not_final_evaluation',
            'version': VERSION, 'started_utc': datetime.now(timezone.utc).isoformat(),
            'models': MODELS, 'seed': SEED, 'python': platform.python_version(),
            'failures': [], 'quality_approved': False, 'wandb_status': 'disabled'}
    def save():
        (args.output/'metadata.json').write_text(json.dumps(meta, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    save()
    wb = None
    out = (args.output/'integration_rows.jsonl').open('w', encoding='utf-8')
    def emit(row):
        out.write(json.dumps(row, ensure_ascii=False)+'\n'); out.flush()
        if wb:
            try:
                c = row.get('result', {}).get('components', {})
                wb.log({row['stage']+'/wall_seconds': row['stage_wall_seconds'],
                        'integration/technical_success': int('error' not in row),
                        'usage/vision': int(c.get('vision', False)), 'usage/tool': int(c.get('tool', False))})
            except Exception:
                meta['wandb_status'] = 'logging_error'
    def attempt(stage, case_id, fn):
        print(f'{stage}: {case_id}', flush=True)
        started = time.perf_counter()
        try:
            row = {'stage': stage, 'case_id': case_id, 'result': fn()}
        except Exception as exc:
            row = {'stage': stage, 'case_id': case_id, 'error': type(exc).__name__, 'detail': str(exc)}
            meta['failures'].append({'stage': stage, 'case_id': case_id, 'error': type(exc).__name__})
        row['stage_wall_seconds'] = time.perf_counter()-started
        emit(row)
        return row
    try:
        import os
        os.environ.setdefault('USE_TF', '0')
        os.environ['GRADIO_ANALYTICS_ENABLED'] = 'False'
        from sqlite_support import ensure_sqlite
        meta['sqlite'] = ensure_sqlite()
        import torch
        import numpy as np
        if not torch.cuda.is_available():
            raise RuntimeError('Activate Colab GPU T4 before running integration')
        random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED); torch.cuda.manual_seed_all(SEED)
        meta.update(gpu=torch.cuda.get_device_name(0),
                    git_commit=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
                    corpus_sha256=sha(ROOT/'m3/corpus/documents.jsonl'),
                    adapter_sha256=sha(ROOT/'model/contractrisk_robertalex_lora_adapter.zip'),
                    source_hashes={str(p.relative_to(ROOT)): sha(p) for p in (ROOT/'final').glob('*.py')},
                    packages={p: importlib.metadata.version(p) for p in
                              ['torch','transformers','peft','accelerate','sentence-transformers','chromadb','numpy','matplotlib','wandb']},
                    memory_policy='classifier CPU; generator and VLM loaded sequentially on GPU',
                    latency_policy='text predict wall time; standalone VLM measured separately; cached visual orchestration excludes VLM; excludes loading; not an efficiency benchmark')
        assert meta['corpus_sha256'] == '7c179b53b87103e6b2992ffda49775bce6118f1ab577c991c4ab5fbb4d234505'
        if os.getenv('WANDB_API_KEY'):
            try:
                import wandb
                wb = wandb.init(entity='jcramonp-eanit', project='contractrisk-final',
                    job_type='development_integration', config={'version': VERSION, 'phase': 'development_only'},
                    settings=wandb.Settings(console='off', disable_git=True, disable_code=True,
                                            disable_job_creation=True, x_disable_stats=True, init_timeout=20))
                meta.update(wandb_status='connected_not_yet_finished', wandb_run_id=wb.id)
            except Exception:
                meta['wandb_status'] = 'connection_error'
        save()
        from final.integration import IntegratedSystem
        from final.adapters import Classifier, AnswerAdapter, Vision
        from rag_basic import DenseRetriever
        from ingest import chunk_documents
        from sentence_transformers import CrossEncoder
        from huggingface_hub import snapshot_download
        documents = [json.loads(line) for line in (ROOT/'m3/corpus/documents.jsonl').read_text(encoding='utf-8').splitlines()]
        fixtures = create_fixtures(documents, args.output/'fixtures')
        for fixture in fixtures:
            fixture['sha256'] = sha(Path(fixture['path']))
        (args.output/'fixture_manifest.json').write_text(json.dumps(fixtures, ensure_ascii=False, indent=2), encoding='utf-8')
        print('Loading M1 classifier on CPU...', flush=True)
        classifier = Classifier()
        classifier_system = IntegratedSystem(documents, None, classifier=classifier)
        for i, text in enumerate(['PRESTAR SERVICIOS PROFESIONALES', 'Adquirir veinte computadores portátiles para las aulas de formación de la entidad.']):
            attempt('classifier', f'class_dev_{i}', lambda text=text: classifier_system.predict('Evalúa la suficiencia descriptiva', mode='sufficiency', description=text))
        print('Building inherited index and reranker...', flush=True)
        chunks = chunk_documents(documents, 220, 30)
        dense = DenseRetriever(chunks, *MODELS['embedding'], include_identity=True)
        reranker_path = snapshot_download(MODELS['reranker'][0], revision=MODELS['reranker'][1],
            allow_patterns=['config.json','model.safetensors','pytorch_model.bin','tokenizer.json','tokenizer_config.json',
                            'special_tokens_map.json','sentencepiece.bpe.model','vocab.*','merges.txt'])
        scorer = CrossEncoder(reranker_path, max_length=512, device='cpu')
        print('Loading text generator...', flush=True)
        answer = AnswerAdapter(documents, dense, scorer)
        system = IntegratedSystem(documents, answer, classifier=classifier)
        questions = ['¿Qué modalidad registra CO1.PCCNTR.1180445?',
            '¿Cuál es la diferencia absoluta entre los valores de CO1.PCCNTR.1180445 y CO1.PCCNTR.1637043? Cita ambos.',
            '¿Qué concluyó la auditoría de ejecución física de CO1.PCCNTR.1637043?',
            '¿Qué modalidad registra CO1.PCCNTR.999999999999?']
        for i, q in enumerate(questions):
            attempt('text', f'text_dev_{i}', lambda q=q: system.predict(q))
        answer.close(); del answer, system; gc.collect(); torch.cuda.empty_cache()
        print('Loading VLM for standalone extraction...', flush=True)
        vision = Vision()
        from PIL import Image
        reads = {}
        for case in fixtures:
            row = attempt('visual_component', case['id'], lambda case=case: {
                'visual': vision.extract(Image.open(case['path']).convert('RGB'))})
            if 'result' in row:
                reads[case['id']] = row['result']['visual']
        vision.close(); del vision; gc.collect(); torch.cuda.empty_cache()
        print('Reloading generator for end-to-end orchestration from saved visual reads...', flush=True)
        answer = AnswerAdapter(documents, dense, scorer)
        for case in fixtures:
            if case['id'] not in reads:
                continue
            class SavedRead:
                def extract(self, image):
                    return reads[case['id']]
            system = IntegratedSystem(documents, answer, classifier, SavedRead())
            # Saved extraction is an explicit component substitution to fit a T4.
            # This stage is NOT fresh simultaneous end-to-end image latency.
            attempt('visual_orchestration_cached', case['id'], lambda case=case, system=system: system.predict(
                case['question'], image=Image.open(case['path']).convert('RGB')))
        answer.close()
        meta.update(status='completed_with_case_errors' if meta['failures'] else 'completed_pending_human_review',
                    final_gold_loaded=False, chunk_count=len(chunks),
                    multimodal_timing_caveat='VLM measured separately; orchestration reuses its saved output. Not production end-to-end latency.')
    except Exception as exc:
        meta.update(status='failed', error=f'{type(exc).__name__}: {exc}')
        (args.output/'traceback.txt').write_text(traceback.format_exc(), encoding='utf-8')
        raise
    finally:
        out.close()
        if wb:
            try:
                wb.summary['execution_status'] = meta['status']
                wb.summary['case_errors'] = len(meta['failures'])
                wb.summary['quality_approved'] = False
                wb.finish()
                if meta['wandb_status'] == 'connected_not_yet_finished':
                    meta['wandb_status'] = 'finished_check_dashboard'
            except Exception:
                meta['wandb_status'] = 'finish_error'
        meta['finished_utc'] = datetime.now(timezone.utc).isoformat()
        save()
    print(json.dumps(meta, indent=2, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
