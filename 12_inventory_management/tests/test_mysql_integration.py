"""Opt-in tests against a separate real MySQL database. No mocking of SQL."""

import os
import unittest
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from uuid import uuid4
from unittest.mock import patch

from inventory.database import Database, settings
from inventory.errors import InventoryError
from inventory.service import InventoryService


@unittest.skipUnless(os.getenv("RUN_MYSQL_TESTS") == "1", "Set RUN_MYSQL_TESTS=1 to use a separate MySQL test database")
class MySQLIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = settings()
        test_database = os.getenv("TEST_MYSQL_DATABASE", "inventory_management_test")
        if not test_database.endswith("_test"):
            raise RuntimeError("TEST_MYSQL_DATABASE must end in _test; refusing to use a normal database.")
        config["database"] = test_database
        cls.database = Database(config)
        cls.database.initialize()

    def setUp(self):
        self.service = InventoryService(self.database)
        self.prefix = "TEST-" + uuid4().hex[:12].upper() + "-"
        self.sku = self.prefix + "001"

    def tearDown(self):
        # Only this test's randomly named products are removed; never truncate.
        with self.database.transaction() as cursor:
            cursor.execute(
                "DELETE m FROM stock_movements m JOIN products p ON p.id = m.product_id WHERE p.sku LIKE %s",
                (self.prefix + "%",),
            )
            cursor.execute("DELETE FROM products WHERE sku LIKE %s", (self.prefix + "%",))

    def add(self, quantity=5):
        return self.service.add(self.sku, "Test Keyboard", "Testing", "199.50", quantity, 3)

    def test_create_read_update_search_and_archive(self):
        product_id = self.add()
        self.assertEqual(self.service.show(self.sku)["id"], product_id)
        self.assertEqual(len(self.service.movements(self.sku)), 1)
        self.service.update(self.sku, name="Updated keyboard", price="205.00", reorder_level=7)
        product = self.service.show(self.sku)
        self.assertEqual(product["name"], "Updated keyboard")
        self.assertEqual(product["price"], Decimal("205.00"))
        self.assertEqual(len(self.service.list(search=self.sku, low_stock=True)), 1)
        with self.assertRaisesRegex(InventoryError, "with stock"):
            self.service.delete(self.sku)
        self.service.adjust(self.sku, -5, "Demo stock removed")
        self.service.delete(self.sku)
        self.assertFalse(self.service.show(self.sku)["active"])
        self.assertEqual(self.service.list(search=self.sku), [])
        self.assertEqual(len(self.service.list(search=self.sku, include_archived=True)), 1)
        self.assertEqual(len(self.service.movements(self.sku)), 2)
        with self.assertRaisesRegex(InventoryError, "archived"):
            self.service.adjust(self.sku, 1, "Not allowed")
        with self.assertRaisesRegex(InventoryError, "archived"):
            self.service.update(self.sku, price="1.00")

    def test_duplicate_sku_is_rejected_without_new_movement(self):
        self.add()
        with self.assertRaisesRegex(InventoryError, "already exists"):
            self.add()
        self.assertEqual(len(self.service.movements(self.sku)), 1)

    def test_failed_stock_removal_preserves_quantity_and_history(self):
        self.add()
        with self.assertRaisesRegex(InventoryError, "Insufficient stock"):
            self.service.adjust(self.sku, -6, "Too much")
        self.assertEqual(self.service.show(self.sku)["quantity"], 5)
        self.assertEqual(len(self.service.movements(self.sku)), 1)

    def test_failed_audit_insert_rolls_back_product_update(self):
        self.add()
        # The real UPDATE runs, then an injected audit error triggers real rollback.
        with patch.object(self.service, "_record_movement", side_effect=RuntimeError("audit failed")):
            with self.assertRaisesRegex(RuntimeError, "audit failed"):
                self.service.adjust(self.sku, 2, "Incoming shipment")
        self.assertEqual(self.service.show(self.sku)["quantity"], 5)
        self.assertEqual(len(self.service.movements(self.sku)), 1)

    def test_competing_removals_cannot_make_stock_negative(self):
        self.add()

        def remove_four():
            try:
                self.service.adjust(self.sku, -4, "Concurrent removal test")
                return "accepted"
            except InventoryError:
                return "rejected"

        with ThreadPoolExecutor(max_workers=2) as executor:
            outcomes = list(executor.map(lambda _: remove_four(), range(2)))
        self.assertCountEqual(outcomes, ["accepted", "rejected"])
        self.assertEqual(self.service.show(self.sku)["quantity"], 1)
        self.assertEqual(len(self.service.movements(self.sku)), 2)

    def test_sql_like_text_is_stored_and_searched_as_data(self):
        name = "Bob's 100% keyboard; SELECT 1"
        self.service.add(self.sku, name, "Testing", "10.00")
        self.assertEqual(self.service.show(self.sku)["name"], name)
        rows = self.service.list(search=name)
        self.assertIn(self.sku, {row["sku"] for row in rows})
        self.assertEqual(self.service.list(search="' OR 1=1 --"), [])
