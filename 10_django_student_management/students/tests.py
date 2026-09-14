from django.test import TestCase,Client
from django.contrib.auth import get_user_model
from .models import Student
class StudentTests(TestCase):
    def setUp(self):
        self.staff=get_user_model().objects.create_user('staff',password='test-only-password',is_staff=True)
        self.data={'roll_number':'s001','name':'Demo Student','email':'demo@example.com','course':'Python','score':'85.50','enrolled':'2026-09-01'}
    def test_anonymous_blocked(self):
        self.assertEqual(self.client.get('/').status_code,302)
        self.client.post('/add/',self.data);self.assertEqual(Student.objects.count(),0)
    def test_nonstaff_blocked(self):
        user=get_user_model().objects.create_user('viewer',password='test-only-password')
        self.client.force_login(user);self.client.post('/add/',self.data);self.assertEqual(Student.objects.count(),0)
    def test_crud_search_and_delete_confirmation(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.post('/add/',self.data).status_code,302)
        record=Student.objects.get();self.assertEqual(record.roll_number,'S001')
        self.assertContains(self.client.get('/?q=Demo'),'Demo Student')
        self.assertNotContains(self.client.get('/?q=Unknown'),'Demo Student')
        self.client.post(f'/{record.pk}/edit/',{**self.data,'score':'90.00'})
        record.refresh_from_db();self.assertEqual(str(record.score),'90.00')
        self.client.get(f'/{record.pk}/delete/');self.assertEqual(Student.objects.count(),1)
        self.client.post(f'/{record.pk}/delete/');self.assertEqual(Student.objects.count(),0)
    def test_score_and_unique_roll_validation(self):
        self.client.force_login(self.staff)
        self.client.post('/add/',{**self.data,'score':'101'});self.assertEqual(Student.objects.count(),0)
        self.client.post('/add/',self.data);self.client.post('/add/',self.data);self.assertEqual(Student.objects.count(),1)
    def test_csrf_required(self):
        client=Client(enforce_csrf_checks=True);client.force_login(self.staff)
        self.assertEqual(client.post('/add/',self.data).status_code,403)
    def test_missing_student(self):
        self.client.force_login(self.staff);self.assertEqual(self.client.get('/999/edit/').status_code,404)
