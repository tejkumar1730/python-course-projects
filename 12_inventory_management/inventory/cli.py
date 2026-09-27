"""Argparse translates terminal input to service calls and readable output."""

import argparse
import sys

from mysql.connector import Error as MySQLError

from .errors import InventoryError
from .seed import seed
from .service import InventoryService


def parser():
    result = argparse.ArgumentParser(description="Python + MySQL inventory portfolio project")
    commands = result.add_subparsers(dest="command", required=True)
    commands.add_parser("init-db", help="Create missing tables in the configured existing database")
    commands.add_parser("seed", help="Add sample products without changing existing SKUs")
    add = commands.add_parser("add", help="Create a product and optional opening stock")
    add.add_argument("sku")
    add.add_argument("name")
    add.add_argument("--category", required=True)
    add.add_argument("--price", required=True)
    add.add_argument("--quantity", type=int, default=0)
    add.add_argument("--reorder-level", type=int, default=5)
    listing = commands.add_parser("list", help="List products")
    listing.add_argument("--all", action="store_true", help="Include archived products")
    commands.add_parser("low-stock", help="List active products at or below their reorder level")
    search = commands.add_parser("search", help="Find active products by literal SKU, name or category substring")
    search.add_argument("text")
    show = commands.add_parser("show", help="Show a product, including archived products")
    show.add_argument("sku")
    update = commands.add_parser("update", help="Change product details; stock uses adjust instead")
    update.add_argument("sku")
    update.add_argument("--name")
    update.add_argument("--category")
    update.add_argument("--price")
    update.add_argument("--reorder-level", type=int)
    adjust = commands.add_parser("adjust", help="Add or remove stock atomically with an audit reason")
    adjust.add_argument("sku")
    adjust.add_argument("change", type=int, help="Positive for stock in, negative for stock out")
    adjust.add_argument("--reason", required=True)
    movements = commands.add_parser("movements", help="Show a product's stock audit history")
    movements.add_argument("sku")
    delete = commands.add_parser("delete", help="Archive a zero-stock product and retain its history")
    delete.add_argument("sku")
    return result


def print_table(rows, columns):
    if not rows:
        print("No records found.")
        return
    rendered = [[str(row.get(column, "")) for column in columns] for row in rows]
    widths = [max(len(column), *(len(row[index]) for row in rendered)) for index, column in enumerate(columns)]
    print(" | ".join(column.ljust(width) for column, width in zip(columns, widths)))
    print("-+-".join("-" * width for width in widths))
    for row in rendered:
        print(" | ".join(value.ljust(width) for value, width in zip(row, widths)))


def main(argv=None):
    args = parser().parse_args(argv)
    service = InventoryService()
    try:
        if args.command == "init-db":
            service.database.initialize()
            print("Tables ready. Existing records were preserved.")
        elif args.command == "seed":
            print(f"Added {seed(service)} sample products. Existing SKUs were preserved.")
        elif args.command == "add":
            product_id = service.add(args.sku, args.name, args.category, args.price, args.quantity, args.reorder_level)
            print(f"Created product #{product_id}.")
        elif args.command in ("list", "search", "low-stock"):
            rows = service.list(
                include_archived=getattr(args, "all", False),
                low_stock=args.command == "low-stock",
                search=getattr(args, "text", None),
            )
            print_table(rows, ["sku", "name", "category", "price", "quantity", "reorder_level", "active"])
        elif args.command == "show":
            for key, value in service.show(args.sku).items():
                print(f"{key}: {value}")
        elif args.command == "update":
            service.update(args.sku, args.name, args.category, args.price, args.reorder_level)
            print("Product details updated.")
        elif args.command == "adjust":
            quantity = service.adjust(args.sku, args.change, args.reason)
            print(f"Stock updated. New quantity: {quantity}.")
        elif args.command == "delete":
            service.delete(args.sku)
            print("Product archived. Stock history was retained.")
        elif args.command == "movements":
            print_table(service.movements(args.sku), ["id", "quantity_change", "quantity_after", "reason", "created_at"])
        return 0
    except InventoryError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except MySQLError as error:
        # Avoid echoing database credentials or raw SQL back to the terminal.
        code = error.errno
        if code in (1044, 1045):
            message = "Database access denied. Check .env credentials and the user's grants."
        elif code == 1049:
            message = "Database does not exist. Create it using the README instructions."
        elif code == 1146:
            message = "Tables are missing. Run python main.py init-db."
        elif code in (2002, 2003, 2005):
            message = "Cannot connect to MySQL. Check that the server is running and host/port are correct."
        else:
            message = f"Database operation failed (MySQL error {code}). Check the server and input, then retry."
        print(f"Error: {message}", file=sys.stderr)
        return 1
