# Bank Management System

Create accounts, deposit, withdraw, transfer, show balances and inspect a transaction ledger. Money is integer paise; failed transfers roll back both the balance and ledger changes.

## Run

Requires Python 3.10+. From this folder:

```console
python app.py open "Demo A"
python app.py open "Demo B"
python app.py deposit 1 1000.50
python app.py transfer 1 250.25 2
python app.py withdraw 2 50
python app.py balance 1
python app.py statement 2
```

## Behavior and limits

Use the account IDs returned by open; examples assume a fresh database. This is an unauthenticated, single-user local learning ledger, not banking software. It never connects to real accounts. Amounts must be positive and have at most two decimal places. Data persists in bank.sqlite3; --db PATH selects another file.

## Learning topics

Input validation, functions, error handling, file/database operations, and separation of business logic from the command-line interface.
