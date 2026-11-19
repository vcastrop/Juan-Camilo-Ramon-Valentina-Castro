"""Pre-model package checks; missing metadata is evidence, not an audit crash."""
import importlib.metadata
import sys

EXPECTED = {
    'gradio': '6.16.0', 'transformers': '4.57.6', 'sentence-transformers': '3.4.1',
    'chromadb': '0.6.3', 'numpy': '2.1.3', 'rank-bm25': '0.2.2', 'sentencepiece': '0.2.1',
    'peft': '0.17.1', 'accelerate': '1.10.1', 'huggingface-hub': '0.36.2',
    'pillow': '11.3.0', 'wandb': '0.31.0'}
if sys.platform == 'linux': EXPECTED['pysqlite3-binary'] = '0.5.4.post2'


def package_versions():
    result = {}
    for name in list(EXPECTED)+['torch']:
        try: result[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: result[name] = None
    return result


def inspect_environment():
    from packaging.requirements import Requirement
    versions = package_versions()
    missing = [name for name, value in versions.items() if value is None]
    mismatched = [name for name, value in EXPECTED.items() if versions[name] is not None and versions[name] != value]
    conflicts = []
    # Validate installed metadata too: testing imports alone missed the original conflict.
    for name in EXPECTED:
        if versions[name] is None: continue
        for raw in importlib.metadata.requires(name) or []:
            requirement = Requirement(raw)
            if requirement.marker and not requirement.marker.evaluate(): continue
            normalized = requirement.name.lower().replace('_', '-')
            if normalized in versions and versions[normalized] is not None:
                if not requirement.specifier.contains(versions[normalized], prereleases=True):
                    conflicts.append({'package': name, 'requires': str(requirement), 'installed': versions[normalized]})
    return {'ready': not (missing or mismatched or conflicts), 'packages': versions,
            'missing': missing, 'mismatched': mismatched, 'conflicts': conflicts}


def require_environment():
    report = inspect_environment()
    if not report['ready']: raise RuntimeError('software_environment_not_ready; inspect environment report')
    return report


if __name__ == '__main__':
    import argparse
    import json
    from pathlib import Path
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = inspect_environment()
    args.output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report['ready'] else 1)
