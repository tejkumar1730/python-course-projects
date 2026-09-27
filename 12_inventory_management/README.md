# Inventory Management System

A small Python command-line portfolio project backed by **MySQL**. It manages products, records stock changes, and shows low-stock items. The code uses explicit SQL so a beginner can follow every operation.

This portfolio implementation was completed in September 2026 with AI assistance. It is a learning project, not evidence of past employment, customers, production deployment, or production scale. Read and practice the code before presenting it as your work; [INTERVIEW.md](INTERVIEW.md) gives honest explanations.

## Features

- Add, list, search, view, update and delete products from the active catalog.
- Deletion means **archive**: only zero-stock products can be archived; their SKU and movement history remain stored. There is no permanent-delete command.
- Record incoming/outgoing stock with a required reason and before/after-consistent audit history.
- Prevent negative stock, duplicate SKUs, blank fields and invalid prices.
- Use a transaction and row lock for safe simultaneous stock updates.
- List products whose quantity is less than or equal to their reorder level.
- Seed five repeat-safe demo products.

## Requirements

- Python 3.11 or newer; Python 3.13 is also suitable.
- MySQL 8.0.16 or newer (InnoDB); setup examples use MySQL 8 syntax.
- MySQL command-line client, or MySQL Workbench to run the setup SQL.
- No Django, browser, ORM or separate login system is used in this project.

## Setup

Run commands from this project's folder. Creating a virtual environment is optional if you already have a suitable one for the repository.

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell blocks activation, use `.\.venv\Scripts\python.exe` wherever the instructions say `python`; changing system execution policy is unnecessary.

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Start your MySQL server. Log in as an administrator (`mysql -u root -p`) and run the SQL below. Choose your own local password. If a `portfolio` account already exists, `CREATE USER IF NOT EXISTS` preserves its existing password, so use that password in `.env`.

```sql
CREATE DATABASE IF NOT EXISTS inventory_management
    CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE USER IF NOT EXISTS 'portfolio'@'localhost' IDENTIFIED BY 'change-me-local-password';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, INDEX, REFERENCES
    ON inventory_management.* TO 'portfolio'@'localhost';
```

Edit `.env` to match the database/user/password you just created. The defaults are database `inventory_management`, user `portfolio`, host `127.0.0.1`, port `3306`. For a nonstandard local server port, change `MYSQL_PORT`. Never commit `.env`.

```bash
python main.py init-db
python main.py seed
python main.py list
python main.py low-stock
```

`init-db` creates missing tables in an existing database and preserves records. It does not create a database or migrate an older schema. `seed` adds only missing sample SKUs; it does not reset changes made to samples.

## Everyday commands

```bash
python main.py add HD-001 "USB Hub" --category Accessories --price 599.00 --quantity 8 --reorder-level 3
python main.py search usb
python main.py show HD-001
python main.py update HD-001 --price 549.00 --name "4-Port USB Hub"
python main.py adjust HD-001 5 --reason "Supplier delivery"
python main.py adjust HD-001 -2 --reason "Two units issued"
python main.py movements HD-001
python main.py low-stock
```

Quantity changes use `adjust`, so every change has a movement record. `update` changes only name, category, price or reorder level. A SKU is a stable identifier and cannot be edited. Money is displayed without a currency symbol; use one consistent currency for all entries (the sample figures can be explained as INR).

To archive a product, first remove its remaining stock with an accurate reason, then use `delete`. Do not invent a stock adjustment just to hide real stock. `list --all`, `show` and `movements` can still inspect archived products; their SKUs cannot be reused. Restoring archives is outside this project's scope.

## Structure and database

```text
main.py                    Entry point
inventory/cli.py           Argument parsing and terminal output
inventory/service.py       CRUD, row locking and stock business rules
inventory/database.py      .env settings, connection/transaction lifecycle
inventory/validation.py    Reusable input checks and Decimal prices
inventory/seed.py           Sample products
inventory/errors.py        Expected business-error class
schema.sql                 Products and stock movement tables
tests/                     Unit tests and opt-in real-MySQL integration tests
DEMO.md                    Repeatable walkthrough and screenshot guidance
INTERVIEW.md               Architecture, request flow, Q&A and honest answers
```

`products` has a unique SKU, descriptive fields, `DECIMAL(10,2)` price, current quantity, reorder level, archive flag and timestamps. `stock_movements` has a foreign key to a product, a signed change, resulting quantity, reason and timestamp. The one-to-many relationship preserves stock history. The application inserts an opening movement only when opening quantity is greater than zero.

One stock adjustment follows this path:

```text
Terminal -> argparse -> validate inputs -> connect -> SELECT ... FOR UPDATE
         -> validate available stock -> UPDATE products -> INSERT movement
         -> COMMIT -> print new quantity
```

Any failure before commit triggers rollback. The connection and cursor are closed. Values go through `%s` parameters rather than string interpolation; the few dynamic SQL column names come from a fixed internal allowlist.

## Tests

Run unit tests without a database:

```bash
python -m unittest discover -s tests -v
```

Real MySQL integration tests are skipped unless enabled. They cover CRUD/archive history, duplicates, negative stock, rollback after an audit failure, two competing stock removals, and SQL-like text. The test suite uses an isolated database whose name must end in `_test`. It creates tables but never creates the database and never truncates data; cleanup targets only test-generated SKUs.

Create a test database once, as a MySQL administrator:

```sql
CREATE DATABASE IF NOT EXISTS inventory_management_test
    CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, INDEX, REFERENCES
    ON inventory_management_test.* TO 'portfolio'@'localhost';
```

PowerShell:

```powershell
$env:RUN_MYSQL_TESTS = '1'
$env:TEST_MYSQL_DATABASE = 'inventory_management_test'
python -m unittest discover -s tests -v
Remove-Item Env:RUN_MYSQL_TESTS
```

Linux/macOS:

```bash
RUN_MYSQL_TESTS=1 TEST_MYSQL_DATABASE=inventory_management_test python -m unittest discover -s tests -v
```

## Scope and troubleshooting

This is a local CLI for one trusted operator. Authentication happens at MySQL using the configured database account; there are no application users, roles, password tables or web sessions. A person with direct database write access can bypass the Python rules. Do not describe it as a secure multi-user production system or an immutable audit system.

Connection failures usually mean the server is stopped, credentials/grants are wrong, the port differs, or the database has not been created. Missing-table errors mean `init-db` has not been run. A duplicate-SKU error can refer to an archived product. A price such as `19.999` is rejected rather than silently rounded. Exit code is `0` for success, `1` for application/database errors, and `2` for malformed command syntax.

Reasonable next improvements are pagination, a restore command, application accounts, schema migrations, database backups and a small web interface. They are ideas, not implemented claims.
