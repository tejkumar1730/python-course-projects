import unittest
from decimal import Decimal

from inventory import validation
from inventory.errors import InventoryError


class ValidationTests(unittest.TestCase):
    def test_sku_normalizes_case_and_whitespace(self):
        self.assertEqual(validation.sku("  usb-001  "), "USB-001")

    def test_sku_rejects_sql_and_spaces(self):
        for value in ("", "has space", "'; DROP TABLE products;--", "x" * 41):
            with self.subTest(value=value), self.assertRaises(InventoryError):
                validation.sku(value)

    def test_money_is_decimal(self):
        self.assertEqual(validation.price("199.50"), Decimal("199.50"))
        self.assertEqual(validation.price("0"), Decimal("0.00"))

    def test_invalid_money_is_rejected(self):
        for value in ("-1", "NaN", "Infinity", "1.999", "abc", "100000000", 1.2, True):
            with self.subTest(value=value), self.assertRaises(InventoryError):
                validation.price(value)

    def test_integer_rejects_negative_float_and_boolean(self):
        for value in (-1, 1.5, True, "2", 2_147_483_648):
            with self.subTest(value=value), self.assertRaises(InventoryError):
                validation.integer(value, "Quantity")

    def test_stock_can_be_added_removed_and_reach_zero(self):
        self.assertEqual(validation.stock_after(5, 3), 8)
        self.assertEqual(validation.stock_after(5, -2), 3)
        self.assertEqual(validation.stock_after(5, -5), 0)

    def test_insufficient_stock_is_rejected(self):
        with self.assertRaisesRegex(InventoryError, "Insufficient stock"):
            validation.stock_after(3, -4)

    def test_zero_change_and_overflow_are_rejected(self):
        with self.assertRaises(InventoryError):
            validation.stock_after(3, 0)
        with self.assertRaises(InventoryError):
            validation.stock_after(validation.MAX_INT, 1)

    def test_reason_and_name_cannot_be_blank_or_too_long(self):
        self.assertEqual(validation.text("  Delivery received  ", "Reason", 255), "Delivery received")
        for value in (" ", "x" * 256, None):
            with self.subTest(value=value), self.assertRaises(InventoryError):
                validation.text(value, "Reason", 255)
