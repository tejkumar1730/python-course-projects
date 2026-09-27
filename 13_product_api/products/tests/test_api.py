from decimal import Decimal
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from products.models import Product


class ProductAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = get_user_model().objects.create_user("tej", password="TestPassword!2026")
        cls.other = get_user_model().objects.create_user("other", password="TestPassword!2026")
        cls.token = Token.objects.create(user=cls.owner)
        cls.product = Product.objects.create(owner=cls.owner, sku="TEJ-001", name="Keyboard", price="799.00", stock=8)
        cls.other_product = Product.objects.create(owner=cls.other, sku="OTHER-001", name="Private item", price="49.00", stock=4)

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        self.list_url = reverse("product-list")
        self.detail_url = reverse("product-detail", args=[self.product.pk])

    def payload(self, **changes):
        data = {"sku": "TEJ-002", "name": "Mouse", "description": "Wireless", "price": "499.50", "stock": 12}
        return {**data, **changes}

    def test_all_crud_endpoints_require_authentication(self):
        self.client.credentials()
        for method, url in [("get", self.list_url), ("post", self.list_url), ("get", self.detail_url),
                            ("put", self.detail_url), ("patch", self.detail_url), ("delete", self.detail_url)]:
            with self.subTest(method=method, url=url):
                response = getattr(self.client, method)(url, {}, format="json")
                self.assertEqual(response.status_code, 401)

    def test_valid_credentials_obtain_working_token(self):
        self.client.credentials()
        response = self.client.post(reverse("api-token"), {"username": "tej", "password": "TestPassword!2026"})
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {response.data['token']}")
        self.assertEqual(self.client.get(self.list_url).status_code, 200)

    def test_wrong_password_does_not_obtain_token(self):
        response = self.client.post(reverse("api-token"), {"username": "tej", "password": "wrong"})
        self.assertEqual(response.status_code, 400)
        self.assertNotIn("token", response.data)

    def test_invalid_token_is_rejected(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token invalid")
        self.assertEqual(self.client.get(self.list_url).status_code, 401)

    def test_list_contains_only_own_products(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["sku"], "TEJ-001")

    def test_other_users_product_is_hidden_for_every_detail_operation(self):
        url = reverse("product-detail", args=[self.other_product.pk])
        for method in ["get", "put", "patch", "delete"]:
            with self.subTest(method=method):
                response = getattr(self.client, method)(url, self.payload(), format="json")
                self.assertEqual(response.status_code, 404)
        self.other_product.refresh_from_db()
        self.assertEqual(self.other_product.name, "Private item")

    def test_create_sets_authenticated_owner_and_decimal_price(self):
        response = self.client.post(self.list_url, self.payload(owner="other"), format="json")
        self.assertEqual(response.status_code, 201)
        product = Product.objects.get(pk=response.data["id"])
        self.assertEqual(product.owner, self.owner)
        self.assertEqual(product.price, Decimal("499.50"))

    def test_read_one_product(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Keyboard")

    def test_put_replaces_editable_required_fields(self):
        response = self.client.put(self.detail_url, self.payload(sku="TEJ-001"), format="json")
        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Mouse")

    def test_put_requires_fields(self):
        response = self.client.put(self.detail_url, {"name": "Mouse"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("sku", response.data)
        self.assertIn("price", response.data)

    def test_patch_changes_only_supplied_fields_and_preserves_owner(self):
        response = self.client.patch(self.detail_url, {"stock": 3, "owner": "other"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        self.assertEqual(self.product.name, "Keyboard")
        self.assertEqual(self.product.owner, self.owner)

    def test_delete_removes_product(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())

    def test_invalid_values_return_field_errors_without_creating_rows(self):
        cases = [
            ("name", ""), ("name", "   "), ("name", "x" * 121),
            ("sku", ""), ("sku", "lowercase"), ("sku", "BAD SKU"), ("sku", "X" * 33),
            ("price", "-0.01"), ("price", "10.123"), ("price", "100000000.00"), ("price", "not-money"),
            ("stock", -1), ("stock", "1.5"), ("stock", 2147483648),
            ("description", "x" * 2001),
        ]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                response = self.client.post(self.list_url, self.payload(**{field: value}), format="json")
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
        self.assertEqual(Product.objects.count(), 2)

    def test_zero_price_and_stock_are_valid(self):
        response = self.client.post(self.list_url, self.payload(price="0.00", stock=0), format="json")
        self.assertEqual(response.status_code, 201)

    def test_duplicate_sku_is_rejected_on_create(self):
        response = self.client.post(self.list_url, self.payload(sku="TEJ-001"), format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("sku", response.data)

    def test_duplicate_sku_is_rejected_on_update(self):
        response = self.client.patch(self.detail_url, {"sku": "OTHER-001"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.product.refresh_from_db()
        self.assertEqual(self.product.sku, "TEJ-001")

    def test_search_does_not_leak_other_users_products(self):
        response = self.client.get(self.list_url, {"search": "Private"})
        self.assertEqual(response.data["count"], 0)
        response = self.client.get(self.list_url, {"search": "keyboard"})
        self.assertEqual(response.data["count"], 1)

    def test_ordering_by_price(self):
        Product.objects.create(owner=self.owner, sku="TEJ-CHEAP", name="Pen", price="20.00", stock=1)
        response = self.client.get(self.list_url, {"ordering": "price"})
        self.assertEqual([row["sku"] for row in response.data["results"]], ["TEJ-CHEAP", "TEJ-001"])

    def test_list_is_paginated(self):
        Product.objects.bulk_create([
            Product(owner=self.owner, sku=f"PAGE-{number}", name=f"Item {number}", price="1.00", stock=1)
            for number in range(12)
        ])
        response = self.client.get(self.list_url)
        self.assertEqual(response.data["count"], 13)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertIsNotNone(response.data["next"])
        self.assertEqual(len(self.client.get(self.list_url, {"page": 2}).data["results"]), 3)

    def test_missing_product_returns_404(self):
        response = self.client.get(reverse("product-detail", args=[999999]))
        self.assertEqual(response.status_code, 404)

    def test_inactive_user_cannot_log_in(self):
        self.owner.is_active = False
        self.owner.save()
        response = self.client.post(reverse("api-token"), {"username": "tej", "password": "TestPassword!2026"})
        self.assertEqual(response.status_code, 400)


class DemoSeedTests(APITestCase):
    def test_seed_can_be_repeated_without_duplicate_rows_or_password_changes(self):
        call_command("seed_demo", password="LocalDemo!2026", stdout=StringIO())
        call_command("seed_demo", password="Different!2026", stdout=StringIO())
        self.assertEqual(Product.objects.count(), 3)
        user = get_user_model().objects.get(username="tej_demo")
        self.assertTrue(user.check_password("LocalDemo!2026"))

    def test_missing_password_does_not_leave_a_partial_account(self):
        with self.assertRaises(CommandError):
            call_command("seed_demo", stdout=StringIO())
        self.assertFalse(get_user_model().objects.filter(username="tej_demo").exists())

    def test_seed_does_not_take_products_from_another_user(self):
        call_command("seed_demo", password="LocalDemo!2026", stdout=StringIO())
        with self.assertRaises(CommandError):
            call_command("seed_demo", username="second_demo", password="LocalDemo!2026", stdout=StringIO())
        self.assertFalse(get_user_model().objects.filter(username="second_demo").exists())
        self.assertEqual(Product.objects.count(), 3)
