"""Local serial spending guard. No network calls, prices or provider guarantees assumed."""
from contextlib import contextmanager
from decimal import Decimal,InvalidOperation
import json
import os
from pathlib import Path
import uuid


def money(value):
    try:result=Decimal(str(value))
    except InvalidOperation:raise ValueError('Invalid money amount') from None
    if not result.is_finite() or result<0:raise ValueError('Money must be finite and nonnegative')
    return result


class BudgetLedger:
    def __init__(self,path):
        self.path=Path(path);self.lock=self.path.with_suffix(self.path.suffix+'.lock')

    @contextmanager
    def transaction(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        # No stale-lock recovery or concurrent API dispatch: require explicit investigation.
        descriptor=os.open(self.lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
        try:
            data=json.loads(self.path.read_text(encoding='utf-8')) if self.path.exists() else {'version':1,'limit_usd':'5.00','requests':{}}
            if money(data['limit_usd'])!=Decimal('5.00'):raise ValueError('Ledger differs from authorized ceiling')
            yield data
            temp=self.path.with_suffix(self.path.suffix+'.tmp')
            temp.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
            os.replace(temp,self.path)
        finally:
            os.close(descriptor);self.lock.unlink()

    def reserve(self,worst_case_usd):
        amount=money(worst_case_usd)
        with self.transaction() as data:
            if data.get('blocked'):raise RuntimeError('Ledger blocked pending billing investigation')
            used=sum((money(r['charged_or_reserved_usd']) for r in data['requests'].values()),Decimal(0))
            if used+amount>money(data['limit_usd']):raise RuntimeError('Authorized total API budget would be exceeded')
            request_id=uuid.uuid4().hex
            data['requests'][request_id]={'status':'reserved_before_dispatch','charged_or_reserved_usd':str(amount),
                                          'worst_case_usd':str(amount)}
        return request_id

    def settle(self,request_id,actual_usd):
        amount=money(actual_usd)
        exceeded=False
        with self.transaction() as data:
            row=data['requests'][request_id]
            if row['status']!='reserved_before_dispatch':raise ValueError('Request already settled')
            exceeded=amount>money(row['worst_case_usd'])
            row.update(status='reservation_exceeded' if exceeded else 'settled_from_verified_usage',charged_or_reserved_usd=str(amount))
            if exceeded:data['blocked']=True
        if exceeded:raise RuntimeError('Actual charge exceeded reservation; ledger blocked before any further call')

    def used_or_reserved(self):
        with self.transaction() as data:
            return sum((money(r['charged_or_reserved_usd']) for r in data['requests'].values()),Decimal(0))

    # No refund on timeout/network failure: the provider may already have generated/billed.
