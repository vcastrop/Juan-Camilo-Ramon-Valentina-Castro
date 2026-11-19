"""Verify that the failed comparison had no evaluated responses before restarting it."""
import hashlib,json,zipfile
from pathlib import Path
from final.prepare_eval_final import canonical_hash

ARCHIVE_SHA256='7863af2a4126fd5f445d1912a94210538a018d2727516f7b65ae204f61473a11'


def verify(root,settings,pack,domain_rules):
    archive=Path(root)/'final/evidence/comparison_01/original_results.zip'
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=ARCHIVE_SHA256:raise ValueError('Failed comparison evidence changed')
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise ValueError('Failed comparison archive corrupted')
        meta=json.loads(z.read('metadata.json'))
        if meta['git_commit']!='882985171cc4a70d37857f59f78483a7bb76a012' or meta['stage']!='qa_no_rag_fp16:warmup':raise ValueError('Unexpected failed checkpoint')
        if meta['profiles_completed'] or any(name.endswith('predictions.jsonl') for name in z.namelist()):raise ValueError('Prior evaluated responses require explicit reuse')
        previous=json.loads(z.read('collection_settings.json'));current=dict(settings)
        if current.pop('version')!='common-collection-1.0.1-callable-fix':raise ValueError('Unexpected repair version')
        if previous.pop('version')!='common-collection-1' or current!=previous:raise ValueError('Repair changed inference settings')
        for key in ['inputs_sha256','references_sha256']:
            actual=pack['inputs_canonical_sha256' if key=='inputs_sha256' else 'references_canonical_sha256']
            if meta[key]!=actual:raise ValueError('Evaluation package changed')
        if meta['domain_rules_sha256']!=canonical_hash(domain_rules):raise ValueError('Domain rules changed')
    return {'archive_sha256':ARCHIVE_SHA256,'previous_evaluated_rows':0,
        'settings_changed_except_version':False,'resampling_valid_answers':False,
        'repair':'M3 factory functions are called directly through a predict adapter, not treated as objects with predict'}
