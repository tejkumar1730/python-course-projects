# Interview preparation: Inventory Management System

This portfolio version was built in September 2026 with AI assistance. Speak only about work you have actually run, understood and modified. Do not invent earlier completion dates, internship usage, business users, performance results or production incidents. If a previous resume description suggests the project was finished before it really was, clarify that its working portfolio implementation was completed recently.

## A truthful introduction

After you have practiced the demo and understood the code:

> I recently completed a Python and MySQL inventory portfolio project. It is a command-line application that adds and updates products, searches the catalog, tracks stock and shows low-stock items. I used parameterized SQL, input validation and a transaction so a stock change and its history entry stay consistent. I used AI assistance while building it, then reviewed the code and tested the workflows. It has not been deployed for a real business.

If you have not yet reviewed or tested it, say: "I am currently completing the project and learning the transaction and validation parts." Change the introduction as your actual understanding grows.

## Architecture

The layers are deliberately small:

1. `main.py` calls the CLI entry point.
2. `inventory/cli.py` uses Python's argparse to convert commands into arguments, call the service, show tables, and convert expected failures into readable messages and exit codes.
3. `inventory/service.py` contains product CRUD and stock rules. It directly issues readable SQL; there is no ORM.
4. `inventory/validation.py` validates SKU, strings, integer ranges, prices and resulting stock.
5. `inventory/database.py` reads environment settings, opens connections and manages commit/rollback/cleanup.
6. `inventory/seed.py` supplies small sample records.

There is no HTTP request, browser route or web session. In this project, "request flow" means a command moving through these layers.

## Database schema

| Table | Important columns | Why they exist |
| --- | --- | --- |
| `products` | `id` primary key; unique `sku`; `name`; `category`; `price DECIMAL(10,2)`; `quantity`; `reorder_level`; `active`; timestamps | Current product details and stock balance |
| `stock_movements` | `id` primary key; `product_id` foreign key; signed `quantity_change`; `quantity_after`; `reason`; timestamp | Explain how a product's balance changed |

One product has many stock movements. `product_id` references `products.id`. The foreign key prevents orphaned history and restricts physical deletion. MySQL unique constraints protect the SKU even if two processes try to add the same one simultaneously. CHECK constraints provide another guard against negative prices/quantities, alongside application checks.

Stock movement examples for opening stock 5, receipt 3 and issue 6:

| Change | Quantity after | Reason |
| --- | --- | --- |
| +5 | 5 | Opening stock |
| +3 | 8 | Received practice shipment |
| -6 | 2 | Issued six demo notebooks |

`quantity_after` makes each entry easy to explain. It duplicates a value that could be derived from prior changes, so it must be written in the same transaction as the product balance. Direct database edits can break that relationship; access control and stronger audit guarantees would be future work.

## Trace a complete command

For `python main.py adjust KB-001 -2 --reason "Two units issued"`:

1. Argparse recognizes `adjust`, an SKU, integer `-2` and a reason string.
2. The service normalizes the SKU and validates the reason/change.
3. The transaction helper opens a MySQL connection with autocommit off.
4. `SELECT * FROM products WHERE sku = %s FOR UPDATE` finds and locks the product row.
5. The service rejects missing/archived products and calculates the new quantity.
6. If sufficient stock exists, it updates `products.quantity`.
7. It inserts a stock movement with change, resulting quantity and reason.
8. The helper commits both writes, closes the cursor/connection and the CLI prints the quantity.
9. If any step before commit raises an exception, the helper rolls back. A failed movement insertion therefore does not leave an unrecorded stock update.

The row lock matters because two processes might otherwise both read quantity 5, both decide to remove 4 and overwrite each other's results. With the lock, the second process checks the quantity after the first committed removal and is rejected.

## CRUD mapping

| Operation | Command | SQL and rule |
| --- | --- | --- |
| Create | `add` | INSERT product; optionally INSERT opening movement in the same transaction |
| Read | `list`, `show`, `search`, `low-stock`, `movements` | SELECT with filters or foreign-key lookup |
| Update details | `update` | UPDATE a fixed set of allowed fields |
| Update quantity | `adjust` | Locked SELECT, UPDATE balance, INSERT history, then COMMIT |
| Delete from active catalog | `delete` | UPDATE `active=FALSE` only when quantity is zero |

Be precise: delete is soft deletion/archive, not SQL DELETE. It preserves stock history and prevents accidental loss. An archived SKU cannot be reused and cannot be restored through the current CLI. That is a deliberate small-scope tradeoff.

## Authentication, validation and errors

- **Authentication:** MySQL authenticates the configured database user. The application has no login/accounts/roles. `.env` is ignored by Git. It is local configuration, not encryption or a secret manager.
- **SQL injection:** Values are supplied as SQL parameters. For example, a name containing an apostrophe is treated as data. Dynamic update column names come only from fixed Python keys, never directly from user input.
- **SKU:** Trim whitespace, uppercase, require 1-40 characters, permit letters/digits/hyphen/underscore, and require a letter/digit first.
- **Price:** Use Decimal and DECIMAL(10,2), reject negative values, NaN/infinity and more than two fractional digits. Binary floating point can represent decimal money imprecisely.
- **Stock:** Whole numbers only, nonnegative stored quantities, nonzero changes, no removal larger than available stock, and signed-INT range checks.
- **Strings:** Trim and enforce database length limits. A blank reason is rejected.
- **Expected errors:** `InventoryError` represents user/business failures. The CLI prints concise messages. Connector exceptions produce configuration/database guidance without echoing credentials.
- **Transaction errors:** Roll back and propagate the exception. Unit tests verify cleanup; real MySQL integration tests verify rollback.

## Common bugs and how to investigate them

| Symptom | Likely cause | Check/fix |
| --- | --- | --- |
| Cannot connect | Server stopped or wrong port/host | Verify the running MySQL service and `.env` |
| Access denied | Wrong password or missing grants | Test the same account in the MySQL client; check the account host |
| Unknown database/table | Setup was incomplete | Create database as admin, then run `init-db` |
| Duplicate SKU even though it is not listed | Product is archived | Run `list --all`; choose a new SKU |
| Price rejected | Negative or more than two decimal places | Enter valid decimal text, such as `12.99` |
| Quantity and history disagree in a badly designed version | Separate commits or direct SQL updates | Keep both writes in one transaction; restrict direct DB edits |
| Concurrent stock removal loses an update | Read-modify-write without a lock | Lock the product row before checking stock |
| SQL breaks on an apostrophe | SQL built by concatenating input | Use connector parameters |
| Re-running seed seems to do nothing | Sample SKUs already exist | Expected: seed preserves existing data rather than resetting it |

Describe these as bugs you know how to prevent or test, unless you personally encountered them. Do not claim a made-up debugging story.

## Likely interview questions and honest answers

**Why did you use a CLI?**

"The project scope was Python and MySQL. A command-line interface let me focus on CRUD, SQL and transactions without adding a web framework. A GUI would be a future extension."

**Why MySQL?**

"Products and movements have a clear relational structure. MySQL supports constraints, joins, transactions and row locking. I wanted to practice SQL directly."

**Why two tables instead of one?**

"The product table stores the current balance; the movement table preserves the sequence of changes. Storing many movements in a single product row would make querying and validation harder."

**What are primary and foreign keys?**

"A primary key uniquely identifies a row. The product ID in each movement is a foreign key that references a valid product, enforcing the relationship."

**What is a transaction?**

"A group of database operations that succeed or fail together. In this app a balance update and its movement insert commit together. If the insert fails, rollback restores the previous balance."

**What is `FOR UPDATE`?**

"It locks the selected InnoDB row until the transaction ends. Another stock update for that product must wait, then check the latest committed quantity. I tested two competing removals, but I have not measured production load."

**Do parameters make the whole app secure?**

"They prevent SQL values from being interpreted as SQL syntax in these queries. They do not provide application authorization, encryption, backups or complete production security."

**How do you calculate low stock?**

"For active products, quantity less than or equal to reorder_level. I use the inclusive boundary so stock exactly at the threshold is visible."

**Why not let `update` change quantity?**

"Quantity changes need an audit reason and a movement entry. Keeping them in `adjust` makes that rule easy to follow."

**How did you test it?**

"There are unit tests for validation and transaction cleanup. The opt-in MySQL suite tests CRUD/archive, duplicates, insufficient stock, rollback after an audit failure, concurrent removals and SQL-like input. I can show the actual results from my environment."

Only say you ran the integration suite after you actually ran it. Its default skipped status is not a successful database test.

**How did AI help?**

"I used AI to help build the initial implementation and documentation. My responsibility is to understand the final code, run it, verify the behavior and explain the design. I can walk through the stock-adjustment function and change a validation rule."

**What would you improve next?**

"I would add a controlled restore flow, pagination, application user roles, migrations and deployment/backup procedures. None of those are part of the current implementation."

**Was this used by a real business?**

"No. This is a portfolio project with synthetic sample data, completed recently to practice Python and MySQL."

## Practice before the interview

1. Run the complete demo and explain each output in your own words.
2. Open `service.py` and trace `adjust` without reading this note aloud.
3. Draw the two-table relationship and write a JOIN to show SKU with movement history.
4. Explain why two decimal places and a nonnegative stock balance are different validation concerns.
5. Add one extra sample product yourself and observe that re-running seed does not overwrite it.
6. Reproduce a rejected stock change, confirm the quantity/history stay unchanged, and run the tests.
7. Practice saying "I have not implemented that yet" when asked about roles, deployment, backups or performance.
