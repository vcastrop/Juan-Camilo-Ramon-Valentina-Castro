"""Experimental OCR-only pixel reader. No corpus/gold/model answer lookup."""
import csv
import hashlib
import io
import json
import math
import re
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

from final.visual_fields import FIELDS, transcription_to_visual, uniform_image
from final.integration import normalized

SETTINGS = {'version': 'ocr-candidate-19', 'language': 'spa+eng', 'oem': 1,
            'psm': [3, 6], 'min_word_confidence': 80.0, 'timeout_per_pass_seconds': 30,
            'max_pixels': 12_000_000, 'retries': 0,
            'note': 'Two layouts of ONE engine; not independent readers or calibrated confidence.'}
CRITICAL = {'id_contrato', 'modalidad', 'valor_cop'}


def parse_tsv(text):
    lines = {}
    for row in csv.DictReader(io.StringIO(text), delimiter='\t'):
        if row.get('level') != '5' or not row.get('text', '').strip(): continue
        confidence = float(row['conf'])
        if not math.isfinite(confidence) or not 0 <= confidence <= 100: raise ValueError('Invalid OCR confidence')
        key = tuple(int(row[k]) for k in ['page_num', 'block_num', 'par_num', 'line_num'])
        lines.setdefault(key, []).append((row['text'].strip(), confidence))
    if not lines: raise ValueError('No OCR words')
    rendered, confidences, current = [], {}, None
    for words in lines.values():
        line = ' '.join(word for word, _ in words)
        rendered.append(line)
        if ':' in line:
            current = FIELDS.get(normalized(line.split(':', 1)[0]))
        if current:
            confidences.setdefault(current, []).extend(conf for _, conf in words)
    raw = json.dumps({'legible': True, 'texto_visible': '\n'.join(rendered)}, ensure_ascii=False)
    parsed, evidence = transcription_to_visual(raw)
    return parsed, evidence, {key: min(values) for key, values in confidences.items()}


def consensus(passes):
    if len(passes) != 2: raise ValueError('Exactly two fixed passes required')
    parsed = [p['parsed'] for p in passes]
    if not all(isinstance(p, dict) for p in parsed): raise ValueError('Missing parsed OCR')
    # No O/0, l/1, ID completion, decimal guessing or digit repair.
    for key in CRITICAL:
        for p in passes:
            if p['evidence'].get(key, {}).get('ambiguous') is True:
                raise ValueError('Ambiguous critical OCR field')
        if parsed[0][key] != parsed[1][key]: raise ValueError('OCR layouts disagree')
        if parsed[0][key] is not None:
            if any(p['confidence'].get(key, -1) < SETTINGS['min_word_confidence'] for p in passes):
                raise ValueError('Low-confidence critical OCR field')
    if parsed[0]['id_contrato'] is None: raise ValueError('Readable matching contract ID required')
    result = dict(parsed[0])
    # Do not carry an unsupported object even if critical fields agree.
    if parsed[0]['objeto'] != parsed[1]['objeto'] or any(p['confidence'].get('objeto', -1) < 80 for p in passes):
        result['objeto'] = None
    return result


class OCRCandidate:
    def __init__(self, executable=None):
        self.executable = executable or shutil.which('tesseract')
        if not self.executable: raise RuntimeError('Install tesseract-ocr and spa/eng language data')
        self.version = subprocess.check_output([self.executable, '--version'], text=True, encoding='utf-8').splitlines()[0]
        if not self.version.startswith('tesseract 5.'):
            raise RuntimeError('This fixed OCR candidate requires Tesseract 5.x')
        languages = subprocess.check_output([self.executable, '--list-langs'], text=True, encoding='utf-8')
        if not {'spa', 'eng'} <= set(languages.splitlines()): raise RuntimeError('Missing spa/eng OCR language data')
        directory = re.search(r'"([^"]+)"', languages)
        self.language_data_sha256 = {}
        if directory:
            for language in ['spa', 'eng']:
                path = Path(directory.group(1))/(language+'.traineddata')
                if path.is_file(): self.language_data_sha256[language] = hashlib.sha256(path.read_bytes()).hexdigest()

    def extract(self, image):
        if image.width*image.height > SETTINGS['max_pixels']: raise ValueError('Image too large')
        start = time.perf_counter()
        if uniform_image(image):
            return {'output': {'legible': False, 'texto_visible': None, 'id_contrato': None,
                    'objeto': None, 'modalidad': None, 'valor_cop': None}, 'parse_error': None,
                    'passes': [], 'reader': SETTINGS['version'], 'vision_model_used': False,
                    'guard': 'uniform_pixels', 'latency_seconds': time.perf_counter()-start}
        observations = []
        with tempfile.TemporaryDirectory(prefix='contractrisk_ocr_') as folder:
            path = Path(folder)/'input.png'
            image.convert('RGB').save(path)
            for mode in SETTINGS['psm']:
                command = [self.executable, str(path), 'stdout', '-l', SETTINGS['language'],
                           '--oem', str(SETTINGS['oem']), '--psm', str(mode), 'tsv']
                # Fixed arguments, no shell, no network, bounded runtime; no user text in command.
                completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True, encoding='utf-8', timeout=SETTINGS['timeout_per_pass_seconds'], check=True)
                try:
                    parsed, evidence, confidence = parse_tsv(completed.stdout)
                    parse_error = None
                except (ValueError, KeyError, TypeError):
                    parsed, evidence, confidence, parse_error = None, {}, {}, 'ocr_parse_failed'
                observations.append({'psm': mode, 'parsed': parsed, 'evidence': evidence,
                                     'confidence': confidence, 'parse_error': parse_error,
                                     'raw_tsv': completed.stdout})
        try:
            output, error = consensus(observations), None
        except ValueError:
            output, error = None, 'ocr_consensus_or_confidence_failed'
        return {'output': output, 'parse_error': error, 'passes': observations,
                'reader': SETTINGS['version'], 'vision_model_used': False,
                'latency_seconds': time.perf_counter()-start}
