"""Create fictional, repeatable local data without resetting existing passwords."""
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from jobs.models import Application, Company, Job, Profile


class Command(BaseCommand):
    help = "Create fictional demo accounts and jobs. For local practice only."

    def add_arguments(self, parser):
        parser.add_argument("--reset-passwords", action="store_true", help="Reset the three reserved demo accounts to the documented local password.")

    @transaction.atomic
    def handle(self, *args, **options):
        users = {}
        for username, name, role in [
            ("demo_candidate", "Tej Demo", Profile.Role.CANDIDATE),
            ("demo_employer", "Asha Demo", Profile.Role.EMPLOYER),
            ("demo_employer_two", "Ravi Demo", Profile.Role.EMPLOYER),
        ]:
            email = f"{username}@example.com"
            user, created = User.objects.get_or_create(username=username, defaults={"first_name": name, "email": email})
            if not created and user.email != email:
                raise CommandError(f"Reserved demo username {username} belongs to another account. No seed changes saved.")
            if created or options["reset_passwords"]:
                user.set_password("LocalDemo!2026")
                user.save()
            profile, _ = Profile.objects.get_or_create(user=user, defaults={"role": role})
            if profile.role != role:
                raise CommandError(f"Demo account {username} has an unexpected role. No seed changes saved.")
            users[username] = user

        company_one, _ = Company.objects.get_or_create(owner=users["demo_employer"], defaults={
            "name": "Northstar Labs", "location": "Hyderabad, India",
            "description": "A fictional product team building useful tools for everyday businesses. These listings are sample data for a portfolio project.",
            "website": "https://example.com",
        })
        company_two, _ = Company.objects.get_or_create(owner=users["demo_employer_two"], defaults={
            "name": "Bloom Digital", "location": "Bengaluru, India",
            "description": "A fictional small studio focused on thoughtful websites and practical software. All opportunities here are demonstration data.",
            "website": "https://example.com",
        })
        samples = [
            (company_one, "Python Backend Intern", "Hyderabad", "internship", 120000, 180000,
             "Learn to build Django views, work with relational data, and write useful tests alongside a small product team.",
             "Python fundamentals, basic SQL, HTML and curiosity about web development. Share a small project you can explain."),
            (company_one, "Junior Django Developer", "Remote", "full_time", 300000, 450000,
             "Help maintain a server-rendered web application. Build forms, fix bugs, and improve the experience for customers.",
             "Comfort with Python functions, Django models and Git basics. Understanding of HTTP and relational database keys."),
            (company_two, "Frontend Developer Intern", "Bengaluru", "internship", 120000, 200000,
             "Turn simple designs into responsive pages with semantic HTML, approachable CSS, and small JavaScript enhancements.",
             "HTML, CSS, basic JavaScript, and an interest in accessible user interfaces."),
            (company_two, "Python Automation Assistant", "Remote", "part_time", 180000, 240000,
             "Create small Python scripts for repeatable office tasks, validate input files, and document how your scripts work.",
             "Python loops, functions, exceptions and file handling. Basic SQL is useful."),
            (company_one, "Junior QA Engineer", "Hyderabad", "full_time", 250000, 380000,
             "Explore web application features, reproduce issues clearly, and help the team turn bug reports into regression tests.",
             "Attention to detail, clear writing, Python basics, and familiarity with browser developer tools."),
            (company_two, "Database Support Intern", "Chennai", "internship", 100000, 160000,
             "Practice writing SQL queries, checking sample datasets, and documenting database tables for a small application.",
             "SQL SELECT, JOIN, GROUP BY, primary and foreign keys, and basic Python."),
        ]
        first_job = None
        for company, title, location, job_type, low, high, description, requirements in samples:
            job, _ = Job.objects.get_or_create(company=company, title=title, defaults={
                "location": location, "employment_type": job_type,
                "salary_min": low, "salary_max": high, "description": description,
                "requirements": requirements, "closing_date": timezone.localdate() + timedelta(days=45),
            })
            first_job = first_job or job
        Application.objects.get_or_create(job=first_job, candidate=users["demo_candidate"], defaults={
            "cover_letter": "I am building small Python and Django portfolio projects and would like to learn how a development team reviews and ships useful features.",
            "status": Application.Status.REVIEWED,
        })
        self.stdout.write(self.style.SUCCESS("Demo ready: 3 accounts, 2 companies, 6 sample roles, 1 sample application. Existing records are preserved."))
        self.stdout.write("New demo accounts use LocalDemo!2026. Existing passwords are unchanged unless --reset-passwords was supplied.")
