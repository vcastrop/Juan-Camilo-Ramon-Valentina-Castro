"""Verify the bounded runtime archive before importing any packaged Python."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import zipfile

MAX_BYTES = 30_000_000


def unpack(archive, expected_sha, destination):
    archive, destination = Path(archive), Path(destination)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != expected_sha:
        raise ValueError('Payload checksum mismatch')
    if destination.exists() and any(destination.iterdir()):
        raise ValueError('Use a new empty payload directory')
    with zipfile.ZipFile(archive) as z:
        infos = z.infolist()
        names = [i.filename for i in infos]
        if len(names) != len(set(names)) or len(names) > 150 or sum(i.file_size for i in infos) > MAX_BYTES:
            raise ValueError('Unexpected archive extent')
        for i in infos:
            p = PurePosixPath(i.filename)
            if (p.is_absolute() or '..' in p.parts or '\\' in i.filename or ':' in i.filename
                    or i.is_dir() or stat.S_ISLNK(i.external_attr >> 16)):
                raise ValueError('Unsafe archive entry')
        manifest = json.loads(z.read('manifest.json'))
        if set(names) != set(manifest['files']) | {'manifest.json'}:
            raise ValueError('Unexpected manifest files')
        for name, sha in manifest['files'].items():
            if hashlib.sha256(z.read(name)).hexdigest() != sha:
                raise ValueError('Runtime file checksum mismatch')
        destination.mkdir(parents=True, exist_ok=True)
        # No code executes before all members, paths and hashes are verified.
        z.extractall(destination)
    return manifest
