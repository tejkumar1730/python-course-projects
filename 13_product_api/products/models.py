from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


class Product(models.Model):
    """A product belongs to exactly one account; SKU is globally unique."""

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products")
    sku = models.CharField(
        max_length=32, unique=True,
        validators=[RegexValidator(r"^[A-Z0-9][A-Z0-9_-]*$", "Use uppercase letters, digits, hyphens or underscores.")],
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, max_length=2000)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.CheckConstraint(condition=models.Q(price__gte=0), name="product_price_nonnegative"),
            models.CheckConstraint(condition=models.Q(stock__gte=0), name="product_stock_nonnegative"),
        ]

    def __str__(self):
        return f"{self.sku}: {self.name}"
