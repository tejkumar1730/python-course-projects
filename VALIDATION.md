# Validation record

Verified locally on 2026-09-14 using Python 3.12.14 and Django 5.2.17.

- Standard-library test suite: 16 tests passed.
- Django portfolio: 4 tests passed; system checks reported no issues.
- Django student management: 6 tests passed; system checks reported no issues.
- Fresh SQLite migrations completed for both Django projects.
- Dictionary, billing, EDA and offline scraper command-line demonstrations exited successfully.
- EDA JSON and HTML report files were created successfully from the synthetic sample.
- Browser inspection: audio reader rendered installed voices, entered Reading status and reached Chapter complete. This verifies speech API lifecycle; actual speaker output was not independently listened to.
- Browser inspection: portfolio rendered ten project cards and the contact form. Desktop layout was visually inspected.
- Browser inspection: student application redirected anonymous visitors to the staff login page. Authenticated create/edit/search/delete, nonstaff rejection and CSRF were verified by Django tests.

## Test commands

```console
python -m unittest discover -s tests -v
python 09_django_portfolio/manage.py test portfolio
python 10_django_student_management/manage.py test students
```

No live third-party scrape, public deployment, real ticket booking or real bank operation was performed. Instructor acceptance criteria were not supplied. Browser speech behavior may vary by operating system and installed voices.
