from django.db import IntegrityError, transaction
from rest_framework import filters, serializers, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.throttling import ScopedRateThrottle

from .models import Product
from .serializers import ProductSerializer


class LoginTokenView(ObtainAuthToken):
    """Exchange valid credentials for a DRF token; local throttle limits retries."""

    authentication_classes = []  # Credentials in the body are sufficient here.
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "token"


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "sku", "description"]
    ordering_fields = ["name", "price", "stock", "created_at", "id"]
    ordering = ["-created_at", "-id"]

    def get_queryset(self):
        # This protects list AND individual endpoints from another user's data.
        return Product.objects.filter(owner=self.request.user).select_related("owner")

    def save_product(self, serializer, **kwargs):
        # Two requests can pass serializer uniqueness checks simultaneously.
        # The database still enforces uniqueness; translate that race into 400.
        try:
            with transaction.atomic():
                serializer.save(**kwargs)
        except IntegrityError:
            sku = serializer.validated_data.get("sku", getattr(serializer.instance, "sku", None))
            duplicates = Product.objects.filter(sku=sku)
            if serializer.instance:
                duplicates = duplicates.exclude(pk=serializer.instance.pk)
            if duplicates.exists():
                raise serializers.ValidationError({"sku": ["A product with this SKU already exists."]})
            raise

    def perform_create(self, serializer):
        # Ignore client-supplied owners; ownership comes from authentication.
        self.save_product(serializer, owner=self.request.user)

    def perform_update(self, serializer):
        self.save_product(serializer)
