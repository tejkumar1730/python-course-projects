# Tej's resume portfolio projects

These are learning projects being implemented and verified on **27 September 2026** from the feature descriptions in `Tej_Kumar_Resume_Balanced.pdf`. They are not employment projects or evidence of earlier delivery. The resume PDF and its personal contact details are deliberately not included in this public repository.

| Resume project | Code and setup | Interview notes | Demo |
|---|---|---|---|
| Job Portal Web Application | [11_job_portal](11_job_portal/README.md) | [Walk through the design](11_job_portal/INTERVIEW.md) | [Try the candidate and employer flows](11_job_portal/DEMO.md) |
| Inventory Management System | [12_inventory_management](12_inventory_management/README.md) | [Explain Python and SQL](12_inventory_management/INTERVIEW.md) | [Try stock and product operations](12_inventory_management/DEMO.md) |
| RESTful Product API | [13_product_api](13_product_api/README.md) | [Explain REST and DRF](13_product_api/INTERVIEW.md) | [Try the endpoints](13_product_api/DEMO.md) |

## Choose a first project

Start with **Inventory** to understand Python, validation, SQL and transactions. Then use **Job Portal** to understand a browser request, Django views, templates, sessions and database models. Finish with **Product API** to understand JSON, serializers, status codes and token authentication. These are three independent applications; they do not share business tables or login accounts.

## Install Python dependencies once

Use Python 3.12 (the tested version) for the combined environment. In PowerShell, from the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r portfolio-requirements.txt
```

If `py -3.12` is not available but `python --version` reports a suitable installed version, use `python -m venv .venv`. Activation is optional: use the full `.venv` Python path, which also avoids PowerShell execution-policy issues. After changing into a project folder, that path becomes `..\.venv\Scripts\python.exe`.

On macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r portfolio-requirements.txt
```

`mysqlclient` may require MySQL client headers and compiler tools on Linux/macOS; see the [official installation notes](https://github.com/PyMySQL/mysqlclient#install). A compatible Windows Python 3.12 wheel was used during verification.

## Set up MySQL

Use a local MySQL 8.4 server and follow each project's README, or use the optional Docker setup below. MySQL must be running before migrations, seeding, or Inventory commands. Installing a Python database driver does not install the server.

Optional Docker Desktop route (PowerShell, repository root):

```powershell
Copy-Item .env.mysql.example .env
# Edit .env and choose two local passwords, then:
docker compose up -d
docker compose ps
```

Wait for the service to become healthy. In EACH project folder copy `.env.example` to `.env`, set `MYSQL_USER=portfolio`, `MYSQL_HOST=127.0.0.1`, `MYSQL_PORT=3307`, and `MYSQL_PASSWORD` to the app password chosen above. Keep each project's distinct `MYSQL_DATABASE`. The default port in individual guides is 3306; this optional container uses 3307 to avoid interfering with another MySQL installation.

The container creates all three databases and test database grants on its **first** start. Changing `.env` later does not reset existing database users; manage credentials in MySQL if needed. `docker compose stop` preserves data. Never run volume deletion commands unless you intend to erase your demo data. The container's published port accepts local connections only. This Compose setup is optional and should be checked with `docker compose config` on a machine with Docker installed.

Then follow each project's migration/initialization, seed and launch commands. The web applications support an explicitly selected SQLite demonstration mode as an alternative; SQLite use is not evidence of MySQL experience. Inventory uses real MySQL.

## What to say honestly

The supplied resume assigns July-August or August-September 2026 dates to these projects. This repository does not substantiate those earlier dates. Update the project dates to the period you actually worked on them. Describe a project as complete only after you can run and explain it. Use wording such as:

> I am building these as personal portfolio projects while preparing for interviews. I used AI assistance for the initial implementation and documentation. I am reviewing the code, running the tests, and making changes myself so I can explain the parts I understand. They use sample data and have not been used by real customers.

Adjust that statement to what you have actually done. Do not say you reviewed, tested or independently implemented a part until you have. If asked about an unfamiliar line: "I used assistance for this section. I understand its purpose, but I need to check the exact behavior before answering." Avoid invented clients, users, traffic, teamwork, deployment or performance improvements.

## A practical interview practice sequence

1. Run every documented happy-path demo and one invalid-input example.
2. Draw the database tables and explain one foreign key.
3. Follow one request from input to validation to database to output.
4. Explain the difference between authentication (who are you?) and authorization (what may you access?).
5. Read a failing-test scenario, predict the expected result, then run it.
6. Make one small change yourself: add an Inventory search example, change a Job Portal label, or add a Product API field with a migration and test.
7. Give a two-minute explanation without reading the guide, then answer follow-up questions from the project interview notes.

Use [INTERVIEW_PRACTICE.md](INTERVIEW_PRACTICE.md) for a repeatable checklist, and [PORTFOLIO_VALIDATION.md](PORTFOLIO_VALIDATION.md) for the actual verification record and limitations.

## Reference documentation

- [Django 5.2 documentation](https://docs.djangoproject.com/en/5.2/)
- [Django database support](https://docs.djangoproject.com/en/5.2/ref/databases/)
- [Django REST Framework tutorial](https://www.django-rest-framework.org/tutorial/quickstart/)
- [MySQL Connector/Python guide](https://dev.mysql.com/doc/connector-python/en/)
- [MySQL Community downloads](https://dev.mysql.com/downloads/mysql/)

The code and explanations are intentionally modest. There is no AI integration, paid API, cloud deployment, email service, real applicant data or commercial inventory integration in this scope.
