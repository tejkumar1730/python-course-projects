"""Repeat-safe sample data. Existing SKUs, including archived ones, stay untouched."""

SAMPLE_PRODUCTS = [
    ("KB-001", "USB Keyboard", "Accessories", "699.00", 20, 5),
    ("MS-001", "Wireless Mouse", "Accessories", "449.50", 3, 5),
    ("NB-001", "A5 Notebook", "Stationery", "75.00", 40, 10),
    ("PN-001", "Blue Ballpoint Pen", "Stationery", "10.00", 0, 20),
    ("CB-001", "USB-C Cable", "Accessories", "199.00", 12, 4),
]


def seed(service):
    existing_skus = {product["sku"] for product in service.list(include_archived=True)}
    added = 0
    for product in SAMPLE_PRODUCTS:
        if product[0] not in existing_skus:
            service.add(*product)
            added += 1
    return added
