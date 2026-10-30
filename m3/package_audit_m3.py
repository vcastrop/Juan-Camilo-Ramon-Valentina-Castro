"""Build the upload package without credentials, caches or unrelated experiments."""
import argparse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def build(output):
    paths = list(ROOT.glob('*.py')) + [ROOT/'requirements-development-v2.txt']
    for folder in ['tests', 'corpus', 'eval']:
        paths += [p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    paths += [ROOT/'results/final_m3/harness_rows.jsonl',
              ROOT/'evidence/integration_v5/contractrisk_m3_integracion_v5_resultados.zip',
              ROOT/'evidence/development_v3/contractrisk_m3_desarrollo_v3_resultados.zip']
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', zipfile.ZIP_DEFLATED) as archive:
        for p in sorted(set(paths)):
            archive.write(p, 'm3/'+p.relative_to(ROOT).as_posix())
    print(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    build(parser.parse_args().output)
