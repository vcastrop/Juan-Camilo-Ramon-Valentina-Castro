import tempfile,unittest
from decimal import Decimal
from pathlib import Path
from final.api_budget import BudgetLedger,money


class ApiBudgetTests(unittest.TestCase):
    def test_reservation_blocks_overspend_before_dispatch(self):
        with tempfile.TemporaryDirectory() as temp:
            ledger=BudgetLedger(Path(temp)/'ledger.json');ledger.reserve('4.90')
            with self.assertRaises(RuntimeError):ledger.reserve('0.11')
            self.assertEqual(ledger.used_or_reserved(),Decimal('4.90'))

    def test_same_file_persists_across_runs(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'ledger.json';BudgetLedger(path).reserve('3')
            with self.assertRaises(RuntimeError):BudgetLedger(path).reserve('3')

    def test_verified_usage_settles_but_never_above_reservation(self):
        with tempfile.TemporaryDirectory() as temp:
            ledger=BudgetLedger(Path(temp)/'ledger.json');request=ledger.reserve('1')
            ledger.settle(request,'0.20')
            self.assertEqual(ledger.used_or_reserved(),Decimal('0.20'))
            with self.assertRaises(ValueError):ledger.settle(request,'0')

    def test_unexpected_charge_permanently_blocks_dispatch(self):
        with tempfile.TemporaryDirectory() as temp:
            ledger=BudgetLedger(Path(temp)/'ledger.json');request=ledger.reserve('1')
            with self.assertRaises(RuntimeError):ledger.settle(request,'2')
            self.assertEqual(ledger.used_or_reserved(),Decimal('2'))
            with self.assertRaises(RuntimeError):ledger.reserve('0.01')

    def test_unknown_network_charge_stays_reserved(self):
        with tempfile.TemporaryDirectory() as temp:
            ledger=BudgetLedger(Path(temp)/'ledger.json');ledger.reserve('5')
            with self.assertRaises(RuntimeError):ledger.reserve('0.01')

    def test_lock_prevents_simultaneous_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            ledger=BudgetLedger(Path(temp)/'ledger.json')
            with ledger.transaction():
                with self.assertRaises(FileExistsError):ledger.reserve('1')

    def test_invalid_money_rejected(self):
        for amount in ['NaN','Infinity','-1','abc']:
            with self.assertRaises(ValueError):money(amount)


if __name__=='__main__':unittest.main()
