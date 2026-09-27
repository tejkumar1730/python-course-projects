"""CRUD and stock rules. Every SQL value uses connector parameters (%s)."""

from mysql.connector import IntegrityError

from . import validation as validate
from .database import Database
from .errors import InventoryError


class InventoryService:
    def __init__(self, database=None):
        self.database = database or Database()

    def add(self, sku, name, category, price, quantity=0, reorder_level=5):
        sku = validate.sku(sku)
        name = validate.text(name, "Name", 120)
        category = validate.text(category, "Category", 80)
        price = validate.price(price)
        quantity = validate.integer(quantity, "Quantity")
        reorder_level = validate.integer(reorder_level, "Reorder level")
        try:
            with self.database.transaction() as cursor:
                cursor.execute(
                    "INSERT INTO products (sku, name, category, price, quantity, reorder_level) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (sku, name, category, price, quantity, reorder_level),
                )
                product_id = cursor.lastrowid
                if quantity:
                    self._record_movement(cursor, product_id, quantity, quantity, "Opening stock")
            return product_id
        except IntegrityError as error:
            if error.errno == 1062:
                raise InventoryError(f"SKU {sku} already exists, including archived products.") from None
            raise

    def list(self, include_archived=False, low_stock=False, search=None):
        conditions, params = [], []
        if not include_archived:
            conditions.append("active = TRUE")
        if low_stock:
            conditions.append("quantity <= reorder_level")
        if search is not None:
            search = validate.text(search, "Search", 120)
            # LOCATE performs literal substring search; % and _ are not wildcards.
            conditions.append("(LOCATE(%s, sku) > 0 OR LOCATE(%s, name) > 0 OR LOCATE(%s, category) > 0)")
            params.extend([search, search, search])
        query = "SELECT * FROM products"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY name, id"
        with self.database.transaction() as cursor:
            cursor.execute(query, tuple(params))
            return cursor.fetchall()

    def show(self, sku):
        sku = validate.sku(sku)
        with self.database.transaction() as cursor:
            return self._find(cursor, sku)

    def update(self, sku, name=None, category=None, price=None, reorder_level=None):
        sku = validate.sku(sku)
        changes = {}
        if name is not None:
            changes["name"] = validate.text(name, "Name", 120)
        if category is not None:
            changes["category"] = validate.text(category, "Category", 80)
        if price is not None:
            changes["price"] = validate.price(price)
        if reorder_level is not None:
            changes["reorder_level"] = validate.integer(reorder_level, "Reorder level")
        if not changes:
            raise InventoryError("Provide at least one field to update.")
        with self.database.transaction() as cursor:
            product = self._find(cursor, sku, lock=True)
            self._require_active(product)
            # Column names come only from the fixed dictionary keys above.
            assignments = ", ".join(f"{column} = %s" for column in changes)
            cursor.execute(f"UPDATE products SET {assignments} WHERE id = %s", (*changes.values(), product["id"]))

    def adjust(self, sku, change, reason):
        sku = validate.sku(sku)
        reason = validate.text(reason, "Reason", 255)
        validate.integer(change, "Stock change", minimum=-validate.MAX_INT)
        if change == 0:
            raise InventoryError("Stock change cannot be zero.")
        with self.database.transaction() as cursor:
            # Lock the product until commit so two removals cannot read stale stock.
            product = self._find(cursor, sku, lock=True)
            self._require_active(product)
            new_quantity = validate.stock_after(product["quantity"], change)
            cursor.execute("UPDATE products SET quantity = %s WHERE id = %s", (new_quantity, product["id"]))
            self._record_movement(cursor, product["id"], change, new_quantity, reason)
        return new_quantity

    def delete(self, sku):
        """Soft delete zero-stock products while retaining their movement history."""
        sku = validate.sku(sku)
        with self.database.transaction() as cursor:
            product = self._find(cursor, sku, lock=True)
            self._require_active(product)
            if product["quantity"]:
                raise InventoryError("Cannot archive a product with stock. Adjust stock to zero with a reason first.")
            cursor.execute("UPDATE products SET active = FALSE WHERE id = %s", (product["id"],))

    def movements(self, sku):
        sku = validate.sku(sku)
        with self.database.transaction() as cursor:
            product = self._find(cursor, sku)
            cursor.execute("SELECT * FROM stock_movements WHERE product_id = %s ORDER BY id", (product["id"],))
            return cursor.fetchall()

    @staticmethod
    def _find(cursor, sku, lock=False):
        query = "SELECT * FROM products WHERE sku = %s"
        if lock:
            query += " FOR UPDATE"
        cursor.execute(query, (sku,))
        product = cursor.fetchone()
        if product is None:
            raise InventoryError(f"No product found for SKU {sku}.")
        return product

    @staticmethod
    def _require_active(product):
        if not product["active"]:
            raise InventoryError("This product is archived and cannot be changed.")

    @staticmethod
    def _record_movement(cursor, product_id, change, quantity_after, reason):
        cursor.execute(
            "INSERT INTO stock_movements (product_id, quantity_change, quantity_after, reason) VALUES (%s, %s, %s, %s)",
            (product_id, change, quantity_after, reason),
        )
