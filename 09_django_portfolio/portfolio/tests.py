from django.test import TestCase,Client
from django.core.management import call_command
from .models import Project,ContactMessage
class PortfolioTests(TestCase):
    def test_home_and_idempotent_seed(self):
        call_command('seed_demo');call_command('seed_demo')
        self.assertEqual(Project.objects.count(),10)
        self.assertContains(self.client.get('/'),'Railway reservation')
    def test_contact_saved(self):
        result=self.client.post('/contact/',{'name':'Demo','email':'demo@example.com','message':'Hello'},follow=True)
        self.assertContains(result,'saved to the local portfolio inbox')
        self.assertEqual(ContactMessage.objects.count(),1)
    def test_invalid_contact_not_saved(self):
        result=self.client.post('/contact/',{'name':'','email':'bad','message':''})
        self.assertEqual(result.status_code,200);self.assertEqual(ContactMessage.objects.count(),0)
    def test_csrf_required(self):
        result=Client(enforce_csrf_checks=True).post('/contact/',{'name':'Demo','email':'demo@example.com','message':'Hello'})
        self.assertEqual(result.status_code,403)
