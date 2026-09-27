# Five-minute terminal demo

Complete README setup first. Use synthetic data, not actual store records. Commands work in PowerShell and Bash. Samples use a single currency; the demo amounts can represent INR.

## 1. Show repeat-safe sample data

```bash
python main.py init-db
python main.py seed
python main.py seed
python main.py list
python main.py low-stock
```

On a new database the first seed adds 5 products and the second adds 0. On untouched sample data, `MS-001` (3 remaining, reorder level 5) and `PN-001` (0 remaining, reorder level 20) appear in the low-stock report. Changes from previous demos remain in place.

## 2. Create and edit a product

Use a new SKU suffix if you have already run this demo. Archived SKUs remain reserved.

```bash
python main.py add DEMO-001 "Interview Notebook" --category Stationery --price 99.50 --quantity 5 --reorder-level 2
python main.py show DEMO-001
python main.py search "Interview Notebook"
python main.py update DEMO-001 --price 89.00 --name "Interview A5 Notebook"
```

Explain: argparse accepts inputs; validation checks them; one parameterized INSERT creates the product; opening stock is recorded in the same transaction. Price uses Decimal and MySQL DECIMAL.

## 3. Add and remove stock

```bash
python main.py adjust DEMO-001 3 --reason "Received practice shipment"
python main.py adjust DEMO-001 -6 --reason "Issued six demo notebooks"
python main.py movements DEMO-001
python main.py low-stock
```

Quantities move **5 -> 8 -> 2**. There are three movements including opening stock. The product now appears in the low-stock list because `2 <= 2`.

Explain: `SELECT ... FOR UPDATE` locks this product while the service checks stock, updates quantity and inserts the movement. Both writes commit together.

## 4. Show expected validation failures

Run commands individually; failures deliberately return a nonzero exit code.

```bash
python main.py adjust DEMO-001 -999 --reason "Invalid demonstration"
python main.py adjust DEMO-001 0 --reason "No actual change"
python main.py update DEMO-001 --price 12.999
python main.py add DEMO-001 "Duplicate" --category Stationery --price 1.00
python main.py delete DEMO-001
python main.py show DEMO-001
```

Expected errors: insufficient stock; zero change; too many decimal places; duplicate SKU; cannot archive with stock. The final quantity remains **2** and previous valid data is preserved.

## 5. Archive and retain history

```bash
python main.py adjust DEMO-001 -2 --reason "Removed final demo stock after practice"
python main.py delete DEMO-001
python main.py list
python main.py list --all
python main.py movements DEMO-001
python main.py adjust DEMO-001 1 --reason "Archived products cannot be changed"
```

The product disappears from active listings, remains in `list --all` with `active=0`, and retains four movement records. The final command fails because it is archived.

## Screenshots or recording

Capture three terminal screenshots after running the commands:

1. `list` and `low-stock` after seed.
2. `movements DEMO-001` after successful stock changes.
3. The insufficient-stock error followed by `show DEMO-001` proving the quantity did not change.

Use a wide terminal and increase the font size. Keep `.env`, shell history containing credentials, and administrator connection commands out of screenshots. File names such as `inventory-list.png`, `inventory-movements.png` and `inventory-validation.png` are suitable. Screenshots are evidence of running the app only; do not label them as a customer deployment.

## Optional database view

After logging into MySQL using `mysql -u portfolio -p inventory_management`, these queries help explain the relationship:

```sql
SELECT sku, name, quantity, active FROM products ORDER BY id;
SELECT p.sku, m.quantity_change, m.quantity_after, m.reason
FROM stock_movements AS m
JOIN products AS p ON p.id = m.product_id
ORDER BY m.id;
```

`-p` prompts for the password; do not paste a real password into the command or record it on screen.
