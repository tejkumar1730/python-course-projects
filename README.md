# Python Course Projects

Thirteen learning projects covering Python fundamentals, SQLite, HTML parsing, exploratory data analysis, Django, MySQL and REST APIs. Organized as separate folders in one repository for easy review.

**For the three resume portfolio projects, start with [PORTFOLIO_START_HERE.md](PORTFOLIO_START_HERE.md).** Projects 11-13 were implemented with AI assistance on 27 September 2026 as current personal portfolio work. Each includes setup, sample data, tests, demo instructions and an interview guide. See [PORTFOLIO_VALIDATION.md](PORTFOLIO_VALIDATION.md) for verification evidence.

Projects 01-10 follow the project titles supplied in the course screenshot; projects 11-13 follow the supplied resume's feature descriptions. Detailed instructor rubrics and pending exercises were not supplied. The examples are educational demos with synthetic data.

## Projects

| # | Project | Interface | Main features |
|---|---|---|---|
| 01 | [Dictionary](01_dictionary) | Command line | Offline glossary, typo suggestions, custom words |
| 02 | [Railway reservation](02_railway_reservation) | Command line | Search, seats by date, booking, PNR, cancellation |
| 03 | [Bank management](03_bank_management) | Command line | Accounts, deposits, withdrawals, atomic transfers, ledger |
| 04 | [Supermarket billing](04_supermarket_billing) | Command line | Basket, discounts, decimal totals, receipt export |
| 05 | [Audio ebook reader](05_audio_ebook_reader) | Browser + Python server | TXT import, voices, speed, pause, resume, stop |
| 06 | [To-do list](06_todo_list) | Command line | Persistent tasks, deadlines, priorities, search |
| 07 | [EDA](07_eda) | Command line + HTML report | Missingness, duplicates, numerical and categorical summaries |
| 08 | [Web scraping](08_web_scraping) | Command line | Titles, headings, links, robots-aware single-page fetch |
| 09 | [Django portfolio](09_django_portfolio) | Browser | Project cards, admin editing, local contact inbox |
| 10 | [Django student management](10_django_student_management) | Browser | Staff login, student CRUD, validation, search, pagination |
| 11 | [Job Portal Web Application](11_job_portal) | Browser | Candidate/employer roles, companies, job search, posting and applications |
| 12 | [Inventory Management System](12_inventory_management) | Command line | MySQL product CRUD, validation, transactional stock tracking and movement history |
| 13 | [RESTful Product API](13_product_api) | JSON API + browsable API | Authenticated owner-only product CRUD, serializers, search and pagination |

## Quick start for course projects 01-10 (Windows)

Install Python 3.10 or later, then open a terminal in this folder:

```console
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python 01_dictionary/app.py python
python 04_supermarket_billing/app.py 04_supermarket_billing/basket.json
python 07_eda/app.py 07_eda/sample_sales.csv --output generated/eda
python 08_web_scraping/app.py --file 08_web_scraping/sample.html
```

On macOS/Linux use `python3 -m venv .venv` and `source .venv/bin/activate`. Projects 09-10 need Django; projects 01–08 use the standard library. Projects 11-13 have separate database and dependency instructions in [the portfolio guide](PORTFOLIO_START_HERE.md). Each folder has its own README with commands and limitations.

## Browser projects

```console
python 05_audio_ebook_reader/app.py
python 09_django_portfolio/manage.py migrate
python 09_django_portfolio/manage.py seed_demo
python 09_django_portfolio/manage.py runserver 127.0.0.1:8009
```

Run each server in its own terminal. Audio reader: http://127.0.0.1:8005/. Portfolio: http://127.0.0.1:8009/.

For student management, in a separate terminal:

```console
python 10_django_student_management/manage.py migrate
python 10_django_student_management/manage.py createsuperuser
python 10_django_student_management/manage.py runserver 127.0.0.1:8010
```

Open http://127.0.0.1:8010/ and sign in with the account you created.

## Validation

```console
python -m unittest discover -s tests -v
python 09_django_portfolio/manage.py test portfolio
python 10_django_student_management/manage.py test students
```

Tests cover transactional rollback, capacity limits, persistence, invalid amounts, billing totals, task state changes, CSV quality checks, HTML extraction, Django forms, staff access and CSRF. See [VALIDATION.md](VALIDATION.md) for the actual verification performed.

## Data and scope

Local databases, generated reports, credentials and virtual environments are excluded from Git. The bank and railway projects simulate their domains and have no connection to real financial or ticketing services. The dictionary includes a limited glossary. The audio reader depends on browser speech support and does not import PDF/EPUB. No AI service or paid API key is required. No course certificate or submission verification is implied.

## Study guide

Run the examples, change the sample inputs, inspect validation failures, and read each function before extending it. Suggested next steps: add dictionary vocabulary, support train schedules, add receipt inventory, add richer EDA charts, or extend the Django student model. Be ready to explain SQLite transactions, Decimal arithmetic, forms, migrations, authentication and CSRF during a project review.
