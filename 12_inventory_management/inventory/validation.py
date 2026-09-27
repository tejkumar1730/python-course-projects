"""Keep input checks separate from database access so they are easy to test."""

import re
from decimal import Decimal, InvalidOperation

from .errors import InventoryError

MAX_INT = 2_147_483_647


def text(value, label, max_length):
    if not isinstance(value, str):
        raise InventoryError(f"{label} must be text.")
    value = value.strip()
    if not value or len(value) > max_length:
        raise InventoryError(f"{label} must contain 1 to {max_length} characters.")
    return value


def sku(value):
    value = text(value, "SKU", 40).upper()
    if not re.fullmatch(r"[A-Z0-9][A-Z0-9_-]*", value):
        raise InventoryError("SKU must start with a letter or number; use only letters, numbers, - and _.")
    return value


def integer(value, label, minimum=0, maximum=MAX_INT):
    # bool is a subclass of int, but True is not a meaningful stock count.
    if isinstance(value, bool) or not isinstance(value, int):
        raise InventoryError(f"{label} must be a whole number.")
    if not minimum <= value <= maximum:
        raise InventoryError(f"{label} must be between {minimum} and {maximum}.")
    return value


def price(value):
    # Accept decimal strings rather than binary floating point money values.
    if isinstance(value, (float, bool)):
        raise InventoryError("Price must be supplied as decimal text, for example 199.50.")
    try:
        result = Decimal(value)
    except (InvalidOperation, ValueError, TypeError):
        raise InventoryError("Price must be a valid number, for example 199.50.") from None
    if not result.is_finite() or result < 0 or result > Decimal("99999999.99"):
        raise InventoryError("Price must be between 0 and 99999999.99.")
    if result.as_tuple().exponent < -2:
        raise InventoryError("Price must have at most two decimal places.")
    return result.quantize(Decimal("0.01"))


def stock_after(current_quantity, change):
    integer(current_quantity, "Current quantity")
    integer(change, "Stock change", minimum=-MAX_INT)
    if change == 0:
        raise InventoryError("Stock change cannot be zero.")
    result = current_quantity + change
    if result < 0:
        raise InventoryError(f"Insufficient stock: have {current_quantity}, cannot remove {-change}.")
    if result > MAX_INT:
        raise InventoryError("Resulting stock exceeds the supported whole-number range.")
    return result
