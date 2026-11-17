"""Fresh multimodal integration probe. Inference never opens reference answers."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time
import traceback
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'m3')]
os.environ.setdefault('USE_TF', '0')
os.environ.setdefault('ANONYMIZED_TELEMETRY', 'False')
from final.config import MODELS, SEED, VERSION


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_inputs(pack):
    """Only approved input manifest and image bytes enter inference; no references."""
    approval = json.loads((pack/'human_approval.json').read_text(encoding='utf-8'))
    if digest(pack/'manifest.json') != approval['manifest_sha256']:
        raise ValueError('Input manifest changed after review')
    cases = json.loads((pack/'manifest.json').read_text(encoding='utf-8'))
    if len({c['id'] for c in cases}) != len(cases) or {c['id'] for c in cases} != set(approval['approved_ids']):
        raise ValueError('Missing or duplicate reviewed case')
    inputs = []
    for c in cases:
        path = (pack/c['image']).resolve()
        if not path.is_relative_to(pack.resolve()) or digest(path) != c['sha256']:
            raise ValueError('Image path/hash mismatch')
        inputs.append({'id': c['id'], 'question': c['question'], 'path': path})
    return inputs


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--require-wandb', action='store_true')
    args = p.parse_args()
    if args.output.exists():
        p.error('Use a new output directory')
    args.output.mkdir(parents=True)
    meta = {'status': 'started', 'purpose': 'fresh_visual_integration_probe_not_final_scorecard',
            'protocol': 'visual-probe-1', 'integration_version': VERSION, 'seed': SEED, 'models': MODELS,
            'started_utc': datetime.now(timezone.utc).isoformat(), 'quality_approved': False,
            'references_loaded_by_inference': False, 'wandb_status': 'disabled', 'case_errors': [],
            'timing_policy': 'one excluded historical warmup; ten fresh calls; image decode plus VLM plus retrieval plus generation; model/index load separate; no cached readings',
            'memory_policy': 'CUDA allocated/reserved peaks for this process, not all device memory; CPU memory not measured'}
    wb = answer = vision = None
    def save():
        (args.output/'metadata.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    save()
    try:
        pack = ROOT/'final/eval/visual_candidates_v1'
        cases = load_inputs(pack)
        meta.update(manifest_sha256=digest(pack/'manifest.json'), approval_sha256=digest(pack/'human_approval.json'),
                    git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                    source_hashes={p.name:digest(p) for p in (ROOT/'final').glob('*.py')})
        if os.environ.get('WANDB_API_KEY'):
            try:
                import wandb
                wb = wandb.init(entity='jcramonp-eanit', project='contractrisk-final',
                    job_type='fresh-visual-integration-probe', config={'protocol':'visual-probe-1', 'commit':meta['git_commit'], 'cases':len(cases)},
                    settings=wandb.Settings(disable_git=True, disable_code=True, disable_job_creation=True, x_disable_stats=True, init_timeout=30))
                meta.update(wandb_status='connected', wandb_run_id=wb.id, wandb_url=wb.url)
            except Exception:
                meta['wandb_status'] = 'connection_error'
        if args.require_wandb and wb is None:
            raise RuntimeError('W&B unavailable: check WANDB_API_KEY notebook access and entity before loading models; never print the key')
        from sqlite_support import ensure_sqlite
        meta['sqlite'] = ensure_sqlite()
        import torch
        import numpy as np
        from PIL import Image
        if not torch.cuda.is_available():
            raise RuntimeError('Enable a fresh Colab T4 session')
        random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED); torch.cuda.manual_seed_all(SEED)
        meta.update(gpu=torch.cuda.get_device_name(0),
                    packages={n:importlib.metadata.version(n) for n in ['torch','transformers','pillow','wandb']})
        from final.adapters import Vision, AnswerAdapter
        from final.integration import IntegratedSystem
        from rag_basic import DenseRetriever
        from ingest import chunk_documents
        from sentence_transformers import CrossEncoder
        from huggingface_hub import snapshot_download
        corpus = ROOT/'m3/corpus/documents.jsonl'
        meta['corpus_sha256'] = digest(corpus)
        if meta['corpus_sha256'] != '7c179b53b87103e6b2992ffda49775bce6118f1ab577c991c4ab5fbb4d234505':
            raise ValueError('Unexpected corpus snapshot')
        docs = [json.loads(s) for s in corpus.read_text(encoding='utf-8').splitlines()]
        started = time.perf_counter()
        dense = DenseRetriever(chunk_documents(docs,220,30), *MODELS['embedding'], include_identity=True)
        local = snapshot_download(MODELS['reranker'][0], revision=MODELS['reranker'][1],
            allow_patterns=['config.json','model.safetensors','pytorch_model.bin','tokenizer.json','tokenizer_config.json',
                            'special_tokens_map.json','sentencepiece.bpe.model','vocab.*','merges.txt'])
        scorer = CrossEncoder(local, max_length=512, device='cpu')
        print('Loading vision and answer models together; no automatic quantization/fallback.', flush=True)
        vision = Vision()
        answer = AnswerAdapter(docs, dense, scorer)
        system = IntegratedSystem(docs, answer, vision=vision)
        torch.cuda.synchronize()
        meta.update(load_seconds=time.perf_counter()-started, resident_cuda_allocated_bytes=torch.cuda.memory_allocated(),
                    resident_cuda_reserved_bytes=torch.cuda.memory_reserved(), simultaneous_models_loaded=True)
        # Historical image, excluded from new evaluation; neither targets nor new candidates used to tune warmup.
        with zipfile.ZipFile(ROOT/'final/evidence/integration_01/original_results.zip') as z:
            import io
            image = Image.open(io.BytesIO(z.read('fixtures/visual_dev_1.png'))).convert('RGB')
        start = time.perf_counter()
        warmup = system.predict('¿Qué modalidad y valor aparecen en la ficha de la imagen?', image=image)
        torch.cuda.synchronize()
        (args.output/'warmup_excluded.json').write_text(json.dumps({'seconds':time.perf_counter()-start,'result':warmup},ensure_ascii=False)+'\n',encoding='utf-8')
        save()
        with (args.output/'predictions.jsonl').open('w', encoding='utf-8') as stream:
            for c in cases:
                print('Fresh visual request:', c['id'], flush=True)
                torch.cuda.synchronize(); torch.cuda.reset_peak_memory_stats()
                start = time.perf_counter()
                row = {'id':c['id']}
                try:
                    with Image.open(c['path']) as img:
                        row['result'] = system.predict(c['question'], image=img.convert('RGB'))
                except Exception as exc:
                    row.update(error=type(exc).__name__, detail=str(exc))
                    meta['case_errors'].append(c['id'])
                torch.cuda.synchronize()
                row.update(wall_seconds=time.perf_counter()-start, cuda_peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                           cuda_peak_reserved_bytes=torch.cuda.max_memory_reserved())
                stream.write(json.dumps(row, ensure_ascii=False)+'\n'); stream.flush()
                if wb:
                    result = row.get('result', {})
                    try:
                        wb.log({'request/latency_seconds':row['wall_seconds'], 'request/exception_free':int('error' not in row),
                                'usage/vision':int(bool((result.get('visual') or {}).get('vision_model_used'))),
                                'usage/abstention':int(bool((result.get('output') or {}).get('abstencion'))),
                                'usage/tool':int(result.get('components',{}).get('tool',False))})
                    except Exception:
                        meta['wandb_status']='logging_error'
        meta['status'] = 'completed_with_case_errors' if meta['case_errors'] else 'completed_pending_scoring_and_review'
    except Exception as exc:
        meta.update(status='failed', error_type=type(exc).__name__)
        (args.output/'traceback.txt').write_text(traceback.format_exc(), encoding='utf-8')
        raise
    finally:
        for adapter in [answer, vision]:
            if adapter is not None:
                try:
                    adapter.close()
                except Exception:
                    meta['cleanup_error'] = True
        if wb:
            try:
                wb.summary['execution_status'] = meta['status']
                wb.summary['quality_approved'] = False
                wb.finish()
                if meta['wandb_status'] == 'connected':
                    meta['wandb_status'] = 'finished_check_dashboard'
            except Exception:
                meta['wandb_status'] = 'finish_error'
        meta['finished_utc'] = datetime.now(timezone.utc).isoformat()
        save()
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
