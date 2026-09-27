from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["sku", "name", "price", "stock", "owner", "updated_at"]
    search_fields = ["sku", "name"]
    list_filter = ["owner"]
