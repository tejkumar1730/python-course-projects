# Resume portfolio verification

Verified on **27 September 2026** in an isolated local Windows environment by the coding assistant. This records what was run, not work Tej has already personally rehearsed. The three projects use fictional sample data.

## Environment

- Python 3.12.14
- Django 5.2.17, Django REST Framework 3.16.1
- MySQL Community Server 8.4.10, InnoDB, utf8mb4
- mysqlclient 2.3.0, mysql-connector-python 9.7.0, python-dotenv 1.2.3
- The test server was bound to 127.0.0.1 on an isolated port; generated database credentials stayed outside the repository.

## Automated tests actually run

| Project | MySQL result | Additional check |
|---|---|---|
| Job Portal | 20/20 passed | Same 20 passed on SQLite |
| Inventory | 17/17 passed: 11 unit + 6 MySQL integration | Real concurrent stock-removal and forced-failure rollback tests passed |
| Product API | 24/24 passed | Same 24 passed on SQLite |

There are **61 distinct tests** across the three projects. Running the two Django suites on both database engines gives **105 test executions**, not 105 different tests. Both Django system checks and migration-drift checks passed. Dependency consistency check (`pip check`) passed.

Tests exercise authentication and ownership, CRUD, input validation, duplicate constraints, stock rollback, concurrency and sample-data behavior. This is not a load test, penetration test or guarantee of production readiness.

## Setup and demo checks

- Applied initial Django migrations to the MySQL demo databases.
- Job Portal seed twice: three accounts, two companies, six jobs, one sample application; automated seed test also confirms changed passwords are preserved.
- Inventory initialization and seed twice: five active products, then zero additional seed rows. Ran CLI create/update/search/stock movements/low-stock/archive. Rejected an excessive stock removal without changing valid stock.
- API seed twice: exactly three sample products. Unlike the other seeds, the API seed restores its sample rows to their fixture values; existing passwords and unrelated records are preserved.
- Called the running API over real HTTP: anonymous 401; token login; create 201; retrieve 200; duplicate/negative input 400; successful PUT/PATCH 200; filtered search; delete 204; subsequent 404. The temporary product was deleted. No token was printed, stored in a file or included in a screenshot.
- Used the actual Job Portal browser interface to log in as the candidate, submit a fictional application, view it in the dashboard, sign in as the owning employer and update it to Reviewed.
- Used the API's browser session login to inspect the MySQL-backed product list with HTTP 200.

## Screenshots

The JPEGs are actual local application captures, not design mockups. The browser checks used ports 8011 (Job Portal) and 8013 (API); the API README uses 8002, which is just a different local port choice.

- [Job Portal homepage](11_job_portal/screenshots/home.jpg)
- [Candidate application dashboard](11_job_portal/screenshots/candidate-dashboard.jpg)
- [Employer applicants page](11_job_portal/screenshots/employer-applicants.jpg)
- [Authenticated Product API](13_product_api/screenshots/products.jpg)

Inventory includes a reproducible terminal walkthrough in [DEMO.md](12_inventory_management/DEMO.md); no fabricated terminal screenshot is supplied.

## Practical limits

- Verification used a locally extracted MySQL server, not the optional Docker Compose setup. Docker was not installed here; Compose startup has not been exercised locally.
- The GitHub Actions workflow reproduces the MySQL suites on Linux. Its result is separate from these local test results; do not assume a remote green check until GitHub reports one.
- Windows Python 3.12 setup was exercised. Linux/macOS instructions are provided but have not been manually run in this environment.
- The older ten course projects were preserved and were outside this change's testing scope.
- No public deployment, commercial use, real recruitment, email delivery, backups, browser matrix, automated accessibility audit or performance claim is implied.
- Demo accounts and sample passwords are public artificial data. Configure real secrets for any future use beyond a private local demo.
