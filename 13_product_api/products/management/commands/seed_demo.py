import json
from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from products.models import Product


class Command(BaseCommand):
    help = "Create a demo user and restore three sample products; safe to repeat."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="tej_demo")
        parser.add_argument("--password", help="Required only when creating the user; never printed.")

    @transaction.atomic
    def handle(self, *args, **options):
        user, created = get_user_model().objects.get_or_create(username=options["username"])
        if created:
            if not options["password"]:
                raise CommandError("A new demo user needs --password. Use a local demo password.")
            try:
                validate_password(options["password"], user)
            except ValidationError as error:
                raise CommandError(" ".join(error.messages)) from error
            user.set_password(options["password"])
            user.save()
        samples = Path(__file__).resolve().parents[3] / "sample_data" / "products.json"
        for row in json.loads(samples.read_text(encoding="utf-8")):
            sku = row.pop("sku")
            existing = Product.objects.filter(sku=sku).first()
            if existing and existing.owner_id != user.id:
                raise CommandError(f"{sku} belongs to another user; seed will not transfer ownership.")
            Product.objects.update_or_create(sku=sku, defaults={"owner": user, **row})
        self.stdout.write(self.style.SUCCESS(f"Ready: {user.username}; 3 sample products. Existing password unchanged."))
