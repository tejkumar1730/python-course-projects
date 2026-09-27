from datetime import timedelta
from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import JobForm
from .models import Application, Company, Job, Profile


class PortalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.employer = User.objects.create_user("employer", "employer@example.com", "TestPassword!2026")
        cls.other_employer = User.objects.create_user("other_employer", "other@example.com", "TestPassword!2026")
        cls.candidate = User.objects.create_user("candidate", "candidate@example.com", "TestPassword!2026")
        cls.other_candidate = User.objects.create_user("other_candidate", "candidate2@example.com", "TestPassword!2026")
        for user, role in [(cls.employer, "employer"), (cls.other_employer, "employer"), (cls.candidate, "candidate"), (cls.other_candidate, "candidate")]:
            Profile.objects.create(user=user, role=role)
        cls.company = Company.objects.create(owner=cls.employer, name="Test Labs", location="Hyderabad")
        cls.other_company = Company.objects.create(owner=cls.other_employer, name="Other Labs")
        cls.job = Job.objects.create(company=cls.company, title="Python Intern", location="Hyderabad", employment_type="internship", description="Build Django features.", requirements="Basic Python.")
        cls.job_data = {"title": "Junior Developer", "location": "Remote", "employment_type": "full_time", "description": "Build small Django features.", "requirements": "Python and SQL.", "salary_min": 200000, "salary_max": 300000, "is_active": True}
        cls.letter = "I am learning Python and Django and would like to contribute to this team."

    def test_public_browse_detail_and_combined_filters(self):
        response = self.client.get(reverse("job_list"), {"q": "python", "location": "hyder", "type": "internship"})
        self.assertContains(response, "Python Intern")
        self.assertEqual(response.context["page_obj"].paginator.count, 1)
        self.assertEqual(self.client.get(reverse("job_list"), {"location": "Mumbai"}).context["page_obj"].paginator.count, 0)
        self.assertContains(self.client.get(reverse("job_detail", args=[self.job.pk])), "Build Django features.")

    def test_closed_and_expired_jobs_hidden_from_public(self):
        self.job.is_active = False
        self.job.save()
        self.assertNotContains(self.client.get(reverse("job_list")), "Python Intern")
        self.assertEqual(self.client.get(reverse("job_detail", args=[self.job.pk])).status_code, 404)
        self.job.is_active = True
        self.job.closing_date = timezone.localdate() - timedelta(days=1)
        self.job.save()
        self.assertEqual(self.client.get(reverse("job_list")).context["page_obj"].paginator.count, 0)

    def test_candidate_registration_hashes_password_and_cannot_make_staff(self):
        response = self.client.post(reverse("register"), {"username": "newcandidate", "first_name": "Tej", "email": "tej@example.com", "role": "candidate", "password1": "FreshPortfolio!2026", "password2": "FreshPortfolio!2026", "is_staff": True})
        self.assertRedirects(response, reverse("dashboard"))
        user = User.objects.get(username="newcandidate")
        self.assertTrue(user.check_password("FreshPortfolio!2026"))
        self.assertFalse(user.is_staff)
        self.assertEqual(user.profile.role, "candidate")
        self.assertFalse(Company.objects.filter(owner=user).exists())

    def test_employer_registration_requires_company_and_creates_linked_records(self):
        data = {"username": "newemployer", "first_name": "Asha", "email": "asha@example.com", "role": "employer", "password1": "FreshPortfolio!2026", "password2": "FreshPortfolio!2026"}
        response = self.client.post(reverse("register"), data)
        self.assertFormError(response.context["form"], "company_name", "Enter your company name.")
        self.assertFalse(User.objects.filter(username="newemployer").exists())
        data["company_name"] = "New Labs"
        self.client.post(reverse("register"), data)
        self.assertEqual(User.objects.get(username="newemployer").company.name, "New Labs")

    def test_invalid_role_and_weak_password_rejected(self):
        response = self.client.post(reverse("register"), {"username": "badrole", "first_name": "X", "email": "x@example.com", "role": "admin", "password1": "123", "password2": "123"})
        self.assertIn("role", response.context["form"].errors)
        self.assertIn("password2", response.context["form"].errors)
        self.assertFalse(User.objects.filter(username="badrole").exists())

    def test_protected_routes_require_login_and_correct_role(self):
        self.assertRedirects(self.client.get(reverse("apply", args=[self.job.pk])), reverse("login") + "?next=" + reverse("apply", args=[self.job.pk]))
        self.client.force_login(self.candidate)
        self.assertEqual(self.client.get(reverse("job_create")).status_code, 403)
        self.assertEqual(self.client.get(reverse("company_edit")).status_code, 403)
        self.client.force_login(self.employer)
        self.assertEqual(self.client.post(reverse("apply", args=[self.job.pk]), {"cover_letter": self.letter}).status_code, 403)

    def test_employer_create_update_delete_uses_logged_in_owner(self):
        self.client.force_login(self.employer)
        response = self.client.post(reverse("job_create"), {**self.job_data, "company": self.other_company.pk})
        job = Job.objects.get(title="Junior Developer")
        self.assertRedirects(response, reverse("job_detail", args=[job.pk]))
        self.assertEqual(job.company, self.company)
        self.client.post(reverse("job_edit", args=[job.pk]), {**self.job_data, "title": "Updated Developer"})
        job.refresh_from_db()
        self.assertEqual(job.title, "Updated Developer")
        self.assertEqual(self.client.get(reverse("job_delete", args=[job.pk])).status_code, 200)
        self.assertTrue(Job.objects.filter(pk=job.pk).exists())
        self.client.post(reverse("job_delete", args=[job.pk]))
        self.assertFalse(Job.objects.filter(pk=job.pk).exists())

    def test_other_employer_cannot_edit_delete_or_read_applicants(self):
        self.client.force_login(self.other_employer)
        self.assertEqual(self.client.post(reverse("job_edit", args=[self.job.pk]), self.job_data).status_code, 404)
        self.assertEqual(self.client.post(reverse("job_delete", args=[self.job.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse("applicants", args=[self.job.pk])).status_code, 404)
        self.job.refresh_from_db()
        self.assertEqual(self.job.title, "Python Intern")

    def test_salary_range_and_past_deadline_are_rejected(self):
        form = JobForm(data={**self.job_data, "salary_min": 400000, "salary_max": 200000, "closing_date": timezone.localdate() - timedelta(days=1)})
        self.assertFalse(form.is_valid())
        self.assertIn("salary_max", form.errors)
        self.assertIn("closing_date", form.errors)
        self.assertFalse(JobForm(data={**self.job_data, "salary_min": -1}).is_valid())

    def test_existing_expired_job_can_be_closed(self):
        self.job.closing_date = timezone.localdate() - timedelta(days=1)
        self.job.save()
        form = JobForm(data={**self.job_data, "closing_date": self.job.closing_date, "is_active": False}, instance=self.job)
        self.assertTrue(form.is_valid(), form.errors)

    def test_candidate_apply_once_and_fields_cannot_be_forged(self):
        self.client.force_login(self.candidate)
        data = {"cover_letter": self.letter, "candidate": self.other_candidate.pk, "status": "shortlisted"}
        self.assertRedirects(self.client.post(reverse("apply", args=[self.job.pk]), data), reverse("dashboard"))
        self.client.post(reverse("apply", args=[self.job.pk]), data)
        self.assertEqual(Application.objects.filter(job=self.job).count(), 1)
        application = Application.objects.get(job=self.job)
        self.assertEqual(application.candidate, self.candidate)
        self.assertEqual(application.status, "submitted")

    def test_database_rejects_duplicate_application(self):
        Application.objects.create(job=self.job, candidate=self.candidate, cover_letter=self.letter)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Application.objects.create(job=self.job, candidate=self.candidate, cover_letter=self.letter)

    def test_application_validation_and_closed_role(self):
        self.client.force_login(self.candidate)
        response = self.client.post(reverse("apply", args=[self.job.pk]), {"cover_letter": "too short"})
        self.assertIn("cover_letter", response.context["form"].errors)
        self.assertFalse(Application.objects.exists())
        self.job.is_active = False
        self.job.save()
        self.client.post(reverse("apply", args=[self.job.pk]), {"cover_letter": self.letter})
        self.assertFalse(Application.objects.exists())

    def test_candidate_dashboard_is_private_and_retains_closed_application(self):
        application = Application.objects.create(job=self.job, candidate=self.candidate, cover_letter=self.letter)
        self.job.is_active = False
        self.job.save()
        self.client.force_login(self.candidate)
        self.assertEqual(list(self.client.get(reverse("dashboard")).context["applications"]), [application])
        self.assertEqual(self.client.get(reverse("job_detail", args=[self.job.pk])).status_code, 200)
        self.client.force_login(self.other_candidate)
        self.assertEqual(list(self.client.get(reverse("dashboard")).context["applications"]), [])
        self.assertEqual(self.client.get(reverse("job_detail", args=[self.job.pk])).status_code, 404)

    def test_employer_updates_status_and_rejects_bad_status(self):
        application = Application.objects.create(job=self.job, candidate=self.candidate, cover_letter=self.letter)
        self.client.force_login(self.employer)
        self.assertContains(self.client.get(reverse("applicants", args=[self.job.pk])), self.candidate.email)
        self.client.post(reverse("application_status", args=[application.pk]), {"status": "shortlisted"})
        application.refresh_from_db()
        self.assertEqual(application.status, "shortlisted")
        self.client.post(reverse("application_status", args=[application.pk]), {"status": "made_up_status"})
        application.refresh_from_db()
        self.assertEqual(application.status, "shortlisted")
        self.assertEqual(self.client.get(reverse("application_status", args=[application.pk])).status_code, 405)

    def test_other_employer_cannot_update_application_status(self):
        application = Application.objects.create(job=self.job, candidate=self.candidate, cover_letter=self.letter)
        self.client.force_login(self.other_employer)
        self.assertEqual(self.client.post(reverse("application_status", args=[application.pk]), {"status": "rejected"}).status_code, 404)
        application.refresh_from_db()
        self.assertEqual(application.status, "submitted")

    def test_company_profile_updates_only_current_employers_company(self):
        self.client.force_login(self.employer)
        self.client.post(reverse("company_edit"), {"name": "Updated Labs", "location": "Remote", "website": "https://example.com", "description": "Example team", "owner": self.other_employer.pk})
        self.company.refresh_from_db()
        self.other_company.refresh_from_db()
        self.assertEqual(self.company.name, "Updated Labs")
        self.assertEqual(self.company.owner, self.employer)
        self.assertEqual(self.other_company.name, "Other Labs")

    def test_login_logout_and_csrf_protection(self):
        self.assertTrue(self.client.login(username="candidate", password="TestPassword!2026"))
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        self.assertRedirects(self.client.post(reverse("logout")), reverse("job_list"))
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.employer)
        self.assertEqual(csrf_client.post(reverse("job_delete", args=[self.job.pk])).status_code, 403)
        self.assertTrue(Job.objects.filter(pk=self.job.pk).exists())

    def test_user_content_is_escaped(self):
        self.job.description = '<script>alert("bad")</script>'
        self.job.save()
        response = self.client.get(reverse("job_detail", args=[self.job.pk]))
        self.assertNotContains(response, '<script>alert("bad")</script>')
        self.assertContains(response, "&lt;script&gt;")


class DemoSeedTests(TestCase):
    def test_seed_can_be_run_twice_without_duplicates_or_password_reset(self):
        call_command("seed_demo", stdout=StringIO())
        candidate = User.objects.get(username="demo_candidate")
        candidate.set_password("ChangedLocal!2026")
        candidate.save()
        call_command("seed_demo", stdout=StringIO())
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(Company.objects.count(), 2)
        self.assertEqual(Job.objects.count(), 6)
        self.assertEqual(Application.objects.count(), 1)
        candidate.refresh_from_db()
        self.assertTrue(candidate.check_password("ChangedLocal!2026"))
