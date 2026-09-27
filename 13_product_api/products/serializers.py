from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Product
        fields = ["id", "sku", "name", "description", "price", "stock", "owner", "created_at", "updated_at"]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]
        extra_kwargs = {
            "stock": {"min_value": 0, "max_value": 2147483647},
            "name": {"allow_blank": False},
        }
