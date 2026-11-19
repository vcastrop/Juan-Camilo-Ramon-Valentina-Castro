"""Restore audit history only; never checkout/pull/reset or replace source files."""
import argparse
import json
from pathlib import Path
import subprocess

REQUIRED_COMMITS = (
    '6ec8dcdf22433c632b5eb0e5539401c33b9c923d',
    '71912f1c5755790381a8e39c8a67801bcbf9243d',
    '7afdda0212bf38ad1accd043a968db722569c618',
    'ece58275c2a19abfb6bbd2fe4b507731232e9083',
)


def prepare(root):
    root = Path(root)
    def read(*args):
        return subprocess.check_output(['git', *args], cwd=root, text=True).strip()
    head = read('rev-parse', 'HEAD')
    shallow = read('rev-parse', '--is-shallow-repository') == 'true'
    if shallow:
        subprocess.run(['git', 'fetch', '--unshallow', 'origin', 'Entrega/contractrisk-final'],
                       cwd=root, check=True)
    if read('rev-parse', 'HEAD') != head:
        raise RuntimeError('Source checkout unexpectedly changed')
    if read('rev-parse', '--is-shallow-repository') != 'false':
        raise RuntimeError('Audit history remains incomplete')
    for commit in REQUIRED_COMMITS:
        subprocess.run(['git', 'cat-file', '-e', commit+'^{commit}'], cwd=root, check=True)
    return {'source_commit': head, 'was_shallow': shallow, 'history_complete': True,
            'checkout_unchanged': True, 'historical_commits_verified': list(REQUIRED_COMMITS)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(json.dumps(prepare(args.repo), indent=2))
