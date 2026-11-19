"""Build a minimal checksum-bound HF candidate. Does not upload or call inference."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LICENSE_URL = 'https://huggingface.co/Qwen/Qwen2.5-3B-Instruct/resolve/aa8e72537993ba99e69dfaafa59ed015b17504d1/LICENSE'
LICENSE_SHA = 'ef52482bb785733093dc9a2e8edd8e764c77d12d8e9d8f10a80c9b547d32d0f9'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def local_modules(entries, root=ROOT):
    """Static closure of local imports, including lazy imports; never copy repo data broadly."""
    root = Path(root)
    pending, seen = list(entries), set()
    while pending:
        name = pending.pop()
        if name in seen: continue
        seen.add(name)
        tree = ast.parse((root/name).read_text(encoding='utf-8-sig'))
        for node in ast.walk(tree):
            modules = []
            if isinstance(node, ast.Import): modules = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level: raise ValueError('Relative local imports need explicit handling')
                modules = [node.module] if node.module else []
            for module in modules:
                relative = module.replace('.', '/')+'.py'
                for candidate in [relative, 'm3/'+relative]:
                    if (root/candidate).is_file():
                        pending.append(candidate)
                        break
    for prefix in ['final', 'm3']:
        if any(n.startswith(prefix+'/') for n in seen) and (root/prefix/'__init__.py').is_file():
            seen.add(prefix+'/__init__.py')
    return sorted(seen)


def build(output, license_file=None, source_commit=None):
    from final.service_runtime import verify_assets
    from final.config import MODELS
    verify_assets()
    actual_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if source_commit is not None and source_commit != actual_commit:
        raise ValueError('Requested commit differs from checkout')
    source_commit = actual_commit
    if not re.fullmatch('[a-f0-9]{40}', source_commit): raise ValueError('Invalid commit')
    names = local_modules(['final/service_runtime.py', 'final/service_contract.py', 'final/service_telemetry.py'])
    templates = ['final/space_candidate/app.py', 'final/space_candidate/README.md',
                 'final/space_candidate/requirements.txt', 'final/space_payload.py',
                 'final/build_space_candidate.py']
    # Version really identifies the inference code and template; unrelated docs may be dirty.
    for name in names+templates:
        recorded = subprocess.check_output(['git', 'show', source_commit+':'+name], cwd=ROOT)
        if recorded.replace(b'\r\n', b'\n') != (ROOT/name).read_bytes().replace(b'\r\n', b'\n'):
            raise ValueError('Commit source differs from working copy: '+name)
    license_data = Path(license_file).read_bytes() if license_file else urllib.request.urlopen(LICENSE_URL, timeout=60).read()
    if digest(license_data) != LICENSE_SHA: raise ValueError('Unexpected official license bytes')
    files = {name: (ROOT/name).read_bytes().replace(b'\r\n', b'\n') for name in names}
    for name in ['m3/corpus/documents.jsonl', 'model/contractrisk_robertalex_lora_adapter.zip']:
        files[name] = (ROOT/name).read_bytes()
    files['licenses/QWEN_RESEARCH_LICENSE.txt'] = license_data
    files['NOTICE.txt'] = b'Qwen is licensed under the Qwen RESEARCH LICENSE AGREEMENT, Copyright (c) Alibaba Cloud. All Rights Reserved.\nAcademic research/evaluation only. Built with Qwen.\n'
    manifest = {'source_commit': source_commit, 'precision': 'fp16', 'models': MODELS,
                'files': {name: digest(data) for name, data in files.items()},
                'scope': 'inference only; no gold, judge, saved answers or API keys'}
    files['manifest.json'] = json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2).encode('utf-8')
    output = Path(output)
    if output.exists() and any(output.iterdir()): raise ValueError('Use a new empty output directory')
    output.mkdir(parents=True, exist_ok=True)
    archive = output/'runtime_payload.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 11, 19, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, data)
    template = (ROOT/'final/space_candidate/app.py').read_text(encoding='utf-8')
    bootstrap = (ROOT/'final/space_payload.py').read_text(encoding='utf-8')
    app = template.replace('# __BOOTSTRAP__', bootstrap).replace('__PAYLOAD_SHA__', digest(archive.read_bytes())).replace('__SOURCE_COMMIT__', source_commit)
    (output/'app.py').write_text(app, encoding='utf-8', newline='\n')
    for name in ['README.md', 'requirements.txt']:
        (output/name).write_bytes((ROOT/'final/space_candidate'/name).read_bytes())
    return {'source_commit': source_commit, 'payload_sha256': digest(archive.read_bytes()),
            'payload_files': sorted(files), 'output': str(output)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--license-file', type=Path)
    args = p.parse_args()
    print(json.dumps(build(args.output, args.license_file), indent=2))


if __name__ == '__main__':
    import sys
    sys.path.insert(0, str(ROOT))
    main()
