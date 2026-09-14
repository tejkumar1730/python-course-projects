"""Educational local bank ledger. Amounts are stored in integer paise."""
import argparse
from decimal import Decimal, InvalidOperation
from pathlib import Path
import sqlite3

def paise(value):
    try:
        amount = Decimal(str(value))
        if not amount.is_finite() or amount <= 0 or amount*100 != (amount*100).to_integral_value():
            raise ValueError('Use a positive amount with at most two decimal places.')
        if amount > Decimal('1000000000'): raise ValueError('Amount exceeds demo limit.')
        return int(amount*100)
    except InvalidOperation as error:
        raise ValueError('Invalid amount.') from error

def connect(path):
    db = sqlite3.connect(path); db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.executescript('''
    CREATE TABLE IF NOT EXISTS accounts(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, balance INTEGER NOT NULL DEFAULT 0 CHECK(balance>=0));
    CREATE TABLE IF NOT EXISTS ledger(id INTEGER PRIMARY KEY AUTOINCREMENT, account INTEGER REFERENCES accounts(id), amount INTEGER, note TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP);
    ''')
    return db

def open_account(db, name):
    if not name.strip(): raise ValueError('Account holder is required.')
    with db:
        return db.execute('INSERT INTO accounts(name) VALUES(?)',(name.strip(),)).lastrowid

def transact(db, account, amount, operation, target=None):
    amount = paise(amount)
    if operation not in ('deposit','withdraw','transfer'): raise ValueError('Unknown operation.')
    if operation == 'transfer' and (target is None or target == account): raise ValueError('Choose another destination account.')
    with db:
        db.execute('BEGIN IMMEDIATE')
        if db.execute('SELECT 1 FROM accounts WHERE id=?',(account,)).fetchone() is None: raise ValueError('Account not found.')
        signed = amount if operation == 'deposit' else -amount
        changed = db.execute('UPDATE accounts SET balance=balance+? WHERE id=? AND balance+?>=0',(signed,account,signed))
        if changed.rowcount != 1: raise ValueError('Insufficient funds.')
        db.execute('INSERT INTO ledger(account,amount,note) VALUES(?,?,?)',(account,signed,operation))
        if operation == 'transfer':
            changed = db.execute('UPDATE accounts SET balance=balance+? WHERE id=?',(amount,target))
            if changed.rowcount != 1: raise ValueError('Destination account not found; transfer rolled back.')
            db.execute('INSERT INTO ledger(account,amount,note) VALUES(?,?,?)',(target,amount,f'Transfer from {account}'))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db',default=str(Path(__file__).with_name('bank.sqlite3')))
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('open').add_argument('name')
    for name in ('deposit','withdraw','transfer'):
        cmd=sub.add_parser(name); cmd.add_argument('account',type=int); cmd.add_argument('amount')
        if name=='transfer': cmd.add_argument('target',type=int)
    for name in ('balance','statement'): sub.add_parser(name).add_argument('account',type=int)
    args=p.parse_args(); db=connect(args.db)
    try:
        if args.command=='open': print('Account created:',open_account(db,args.name))
        elif args.command in ('deposit','withdraw','transfer'):
            transact(db,args.account,args.amount,args.command,getattr(args,'target',None)); print('Transaction saved.')
        else:
            row=db.execute('SELECT * FROM accounts WHERE id=?',(args.account,)).fetchone()
            if row is None: raise ValueError('Account not found.')
            print(f"{row['name']} | Balance INR {Decimal(row['balance'])/100:.2f}")
            if args.command=='statement':
                for entry in db.execute('SELECT * FROM ledger WHERE account=? ORDER BY id',(args.account,)):
                    print(f"{entry['created']} | {Decimal(entry['amount'])/100:+.2f} | {entry['note']}")
    except (ValueError,sqlite3.Error) as error: p.exit(1,f'Error: {error}\n')
    finally: db.close()

if __name__=='__main__': main()
