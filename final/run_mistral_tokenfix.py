"""Controlled Mistral rerun: change only chat encoding, not scores/rubric/examples/model."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from final.prepare_eval_final import canonical_hash
from final.calibration_final import cases,ACCEPTANCE
from final.judge_final import rubric_fingerprint
from final.run_second_judge import main as run_regression
from final.generators import NativeChatGenerator


def verify_reference(archive=None):
    archive=archive or ROOT/'final/evidence/judge02_legacy/original_results.zip'
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest!='58c54955f4a195d7fb99e321b1efd79e2e3cb9aa1526d0b95d189966290f7bad':
        raise ValueError('Original Mistral evidence changed')
    with zipfile.ZipFile(archive) as z:
        old=json.loads(z.read('metadata.json'))
        old_rules=json.loads(z.read('regression_summary.json'))['rules']
    config=json.loads((ROOT/'final/judge_second_config.json').read_text(encoding='utf-8'))
    if canonical_hash(config)!=old['config_canonical_sha256']:
        raise ValueError('Checkpoint/inference configuration changed')
    if canonical_hash(cases())!=old['anchors_canonical_sha256'] or rubric_fingerprint()!=old['rubric_sha256']:
        raise ValueError('Rubric or calibration examples changed')
    if canonical_hash(ACCEPTANCE)!=canonical_hash(old_rules):
        raise ValueError('Acceptance rules changed')
    return {'experiment':'mistral-native-chat-1','only_intended_change':'Disable extra special tokens after native chat rendering; assert native token equivalence',
            'reference_archive_sha256':digest,'reference_commit':old['git_commit'],
            'configuration_unchanged':True,'rubric_unchanged':True,'examples_unchanged':True,'acceptance_unchanged':True,
            'confirmation_executed':False,'causality_limit':'CPU proves duplicated BOS in legacy Mistral input, not how much it explains wrong judgements. New scores must be observed.'}


def verify_preflight(path):
    proof=json.loads(path.read_text(encoding='utf-8'))
    if proof.get('passed') is not True or any(proof.get(k)!=38 for k in ['cases','legacy_lengths_match','one_extra_bos_reproduced','corrected_native_matches']):
        raise ValueError('Real tokenizer preflight did not pass all 38 cases')
    config=json.loads((ROOT/'final/judge_second_config.json').read_text(encoding='utf-8'))
    if proof.get('config_canonical_sha256')!=canonical_hash(config) or proof.get('reference_archive_sha256')!=verify_reference()['reference_archive_sha256']:
        raise ValueError('Preflight reference/configuration mismatch')
    for name,digest in proof['source_sha256'].items():
        if name not in ['chat_encoding.py','tokenization_preflight.py','judge_final.py','calibration_final.py'] or hashlib.sha256((ROOT/'final'/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('Tokenization source changed after preflight')
    if set(proof['source_sha256'])!={'chat_encoding.py','tokenization_preflight.py','judge_final.py','calibration_final.py'}:
        raise ValueError('Incomplete source hashes in preflight')
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__=='__main__':
    comparison=verify_reference()
    comparison['tokenizer_preflight_sha256']=verify_preflight(ROOT/'tokenization_preflight.json')
    with zipfile.ZipFile(ROOT/'final/evidence/judge02_legacy/original_results.zip') as z:
        original=json.loads(z.read('metadata.json'))
    comparison.update(reference_gpu=original['gpu'],reference_packages=original['packages'])
    run_regression(generator_class=NativeChatGenerator,controlled_comparison=comparison)
