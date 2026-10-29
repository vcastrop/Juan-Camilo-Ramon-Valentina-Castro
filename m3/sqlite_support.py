"""Select a working SQLite before importing Chroma. Never silently ignore FTS5."""
import importlib
import sys


def check_fts5(module):
    connection = module.connect(':memory:')
    try:
        connection.execute('CREATE VIRTUAL TABLE capability_check USING fts5(text)')
    finally:
        connection.close()


def ensure_sqlite():
    native = importlib.import_module('sqlite3')
    try:
        check_fts5(native)
        selected, backend = native, native.__name__
    except native.OperationalError:
        if 'chromadb' in sys.modules:
            raise RuntimeError('SQLite selection must run before Chroma is imported')
        try:
            selected = importlib.import_module('pysqlite3')
        except ImportError as exc:
            raise RuntimeError('SQLite lacks FTS5; install pysqlite3-binary==0.5.4.post2 on Linux') from exc
        check_fts5(selected)
        sys.modules['sqlite3'] = selected
        backend = 'pysqlite3'
    return {'backend': backend, 'sqlite_version': selected.sqlite_version, 'fts5_checked': True}
