"""Explicitly authorized USD 7 TOTAL ledger; preserve the original USD 5 history."""
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path

from final.api_budget import BudgetLedger, money

AUTHORIZATION = {
    'version': 'user-total-usd7-20261119', 'authorized_total_usd': '7.00',
    'previous_total_usd': '5.00', 'authorization_date_client': '2026-11-19',
    'authorization_source': 'Explicit user message in this chat',
    'user_statement': 'si acepto que el limite suba a 7 continua',
    'additional_usd7_authorized': False, 'unknown_reservations_released': False,
}
BACKUP = 'api_budget_ledger_before_usd7.json'
AUTH_FILE = 'api_budget_authorization_usd7.json'


def _write_exclusive(path, raw):
    with Path(path).open('xb') as stream:
        stream.write(raw)


def migrate(folder, expected_snapshot, *, confirmed_total_usd7=False):
    if not confirmed_total_usd7:
        raise ValueError('Explicit TOTAL USD 7 confirmation required')
    folder = Path(folder)
    path = folder/'api_budget_ledger.json'
    lock = path.with_suffix(path.suffix+'.lock')
    descriptor = os.open(lock, os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    try:
        raw = path.read_bytes()
        before = json.loads(raw)
        if before != expected_snapshot or before.get('limit_usd') != '5.00' or len(before['requests']) != 57:
            raise ValueError('Expected exact confirmation13 cumulative accounting; do not reset')
        if sum(money(r['charged_or_reserved_usd']) for r in before['requests'].values()) != Decimal('4.1974125'):
            raise ValueError('Historical total differs')
        if before.get('blocked'):
            raise ValueError('Investigate blocked ledger before migration')
        _write_exclusive(folder/BACKUP, raw)
        auth = {**AUTHORIZATION, 'migrated_utc': datetime.now(timezone.utc).isoformat(),
                'before_ledger_sha256': hashlib.sha256(raw).hexdigest(), 'prior_entries_preserved': 57}
        _write_exclusive(folder/AUTH_FILE, (json.dumps(auth, indent=2)+'\n').encode())
        after = dict(before, limit_usd='7.00')
        temporary = path.with_suffix('.usd7.migration.tmp')
        _write_exclusive(temporary, (json.dumps(after, indent=2)+'\n').encode())
        os.replace(temporary, path)
        return auth
    finally:
        os.close(descriptor)
        lock.unlink()


class BudgetLedger7(BudgetLedger):
    def validate(self, data):
        if money(data['limit_usd']) != Decimal('7.00'):
            raise ValueError('Ledger differs from authorized USD 7 TOTAL ceiling')
        folder = self.path.parent
        auth = json.loads((folder/AUTH_FILE).read_text(encoding='utf-8'))
        if any(auth.get(k) != v for k, v in AUTHORIZATION.items()):
            raise ValueError('USD 7 authorization missing or changed')
        raw = (folder/BACKUP).read_bytes()
        if hashlib.sha256(raw).hexdigest() != auth['before_ledger_sha256']:
            raise ValueError('Original budget backup changed')
        prior = json.loads(raw)
        if prior['limit_usd'] != '5.00' or len(prior['requests']) != 57:
            raise ValueError('Invalid historical budget backup')
        for key, value in prior['requests'].items():
            if data['requests'].get(key) != value:
                raise ValueError('Historical entries cannot be released or modified')

    @contextmanager
    def transaction(self):
        # Same exclusive lock as the historical ledger. No initialization/reset/recovery.
        descriptor = os.open(self.lock, os.O_CREAT|os.O_EXCL|os.O_WRONLY)
        try:
            data = json.loads(self.path.read_text(encoding='utf-8'))
            self.validate(data)
            yield data
            self.validate(data)
            temporary = self.path.with_suffix('.usd7.transaction.tmp')
            _write_exclusive(temporary, (json.dumps(data, indent=2)+'\n').encode())
            os.replace(temporary, self.path)
        finally:
            os.close(descriptor)
            self.lock.unlink()
