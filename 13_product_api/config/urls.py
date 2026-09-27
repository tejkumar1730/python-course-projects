from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter

from products.views import LoginTokenView, ProductViewSet

router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")

urlpatterns = [
    path("", RedirectView.as_view(url="/api/", permanent=False)),
    path("admin/", admin.site.urls),
    path("api/auth/token/", LoginTokenView.as_view(), name="api-token"),
    path("api-auth/", include("rest_framework.urls")),
    path("api/", include(router.urls)),
]
