"""CPU-only frozen OCR pilot. Does NOT run QA/RAG or authorize public deployment."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'m3')]
from final.ocr_candidate19 import OCRCandidate, SETTINGS
from final.visual_fields import requested_missing

FOLDER = ROOT/'final/evidence/ocr19_protocol'


def sha(data): return hashlib.sha256(data).hexdigest()


def load_protocol():
    protocol = json.loads((FOLDER/'protocol.json').read_text(encoding='utf-8'))
    if protocol['settings'] != SETTINGS or len(protocol['cases']) != 12: raise ValueError('Frozen OCR protocol changed')
    for case in protocol['cases']:
        path = ROOT/case['file']
        if not path.resolve().is_relative_to((ROOT/'final/evidence').resolve()): raise ValueError('Unsafe fixture path')
        if sha(path.read_bytes()) != case['sha256']: raise ValueError('Frozen image changed')
    return protocol


def diagnose(case, result):
    output = result.get('output') or {}
    if result.get('parse_error'): guard = 'visual_schema'
    elif output.get('legible') is False: guard = 'unreadable'
    elif requested_missing('¿Qué modalidad y valor aparecen?', output): guard = 'missing_visual_fields'
    else: guard = 'needs_source_and_answer_validation'
    expected = case['expected']
    exact = bool(expected) and all(output.get(k) == v for k, v in expected.items())
    return {'field_matches': {k: output.get(k) == v for k,v in (expected or {}).items()},
            'all_expected_fields_exact': exact, 'observed_route': guard,
            'expected_route_matches': guard == case['expected_route'],
            'complete_read_automatic_only': bool(case['complete'] and exact and guard == 'needs_source_and_answer_validation'),
            'qa_answer_validated': False, 'human_review': None}


def run(output):
    from PIL import Image
    output = Path(output)
    if output.exists(): raise ValueError('Use a new directory; do not replace previous results')
    output.mkdir(parents=True)
    rows = []
    meta = {'status': 'started', 'purpose': 'post_hoc_ocr_only_pilot_not_integrated_scorecard',
            'api_calls': 0, 'gpu_used': False, 'model_or_prompt_search': False,
            'started_utc': datetime.now(timezone.utc).isoformat(), 'settings': SETTINGS,
            'source_commit': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()}
    try:
        protocol = load_protocol()
        meta['protocol_sha256'] = sha((FOLDER/'protocol.json').read_bytes().replace(b'\r\n',b'\n'))
        reader = OCRCandidate()
        meta['tesseract_version'] = reader.version
        meta['language_data_sha256'] = reader.language_data_sha256
        meta['languages'] = subprocess.check_output([reader.executable,'--list-langs'],text=True)
        for case in protocol['cases']:
            with Image.open(ROOT/case['file']) as image:
                result = reader.extract(image.convert('RGB'))
            row = {'id': case['id'], 'reading': result, 'diagnostics': diagnose(case, result)}
            rows.append(row)
            with (output/'readings.jsonl').open('a',encoding='utf-8') as f:
                f.write(json.dumps(row,ensure_ascii=False)+'\n')
            print(json.dumps(row,ensure_ascii=False),flush=True)
        meta.update(status='completed_requires_review', completed=len(rows),
                    complete_case_denominator=sum(c['complete'] for c in protocol['cases']),
                    complete_reads=sum(r['diagnostics']['complete_read_automatic_only'] for r in rows),
                    routes_matching=sum(r['diagnostics']['expected_route_matches'] for r in rows),
                    public_deployment_approved=False)
    except Exception as exc:
        meta.update(status='failed_partial_evidence_retained',completed=len(rows),error_type=type(exc).__name__)
        raise
    finally:
        (output/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    return meta


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    print(json.dumps(run(parser.parse_args().output),ensure_ascii=False,indent=2))
