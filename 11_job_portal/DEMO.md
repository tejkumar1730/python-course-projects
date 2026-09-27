# Seven-minute Job Portal demonstration

Complete README setup and run `seed_demo`. Start the server at http://127.0.0.1:8011/. Use only fictional demo accounts and cover letters.

## 1. Browse and search

Open the home page while logged out. Six fictional roles are visible. Search for `Python`, then combine a location such as `Hyderabad` and employment type `Internship`. Open Python Backend Intern. Explain that the filters are GET query parameters and Django builds a filtered MySQL query. The site does not call Indeed or scrape vacancies.

## 2. Register an account

Use **Get started** and choose Candidate; the company field is hidden by a small JavaScript enhancement. Switching to Employer shows the required company field. For a repeatable demo, use a new synthetic username and an `example.com` email. The server checks the role/company requirement even if JavaScript is disabled. Registration logs you in; no email is sent.

## 3. Apply as a candidate

Log out using the button, then log in as `demo_candidate` / `LocalDemo!2026`. The dashboard already contains one reviewed application for Python Backend Intern. Browse and choose **Junior Django Developer**, then apply with a cover letter of at least 30 characters, such as:

> I am learning Python, Django and MySQL through portfolio projects. I would like to practise testing, understand code reviews and contribute small features.

Show the character counter. Submit, then show the new entry in the dashboard. Revisit the same job: it shows the existing application instead of letting you create a duplicate. On subsequent demos, choose another unsubmitted role or create a new candidate account.

Explain that the server supplies the candidate ID and submitted status; a client cannot choose another user or shortlist itself.

## 4. Review as the employer

Log out, then sign in as `demo_employer` / `LocalDemo!2026`. The employer dashboard lists only Northstar Labs jobs. Open the applicants link for Junior Django Developer and change the sample application's status to **Reviewed** or **Shortlisted**. Sign back in as the candidate to show that status in the private dashboard.

Only fictional data is used here. This demonstrates a software workflow, not a real hiring decision.

## 5. Show job CRUD

As `demo_employer`, create a job called `Portfolio Demo Role`, with a location, employment type, description and requirements. Try a maximum salary below the minimum and show the validation error, then correct it. Edit the title. Uncheck **Accept applications** and save: the role closes and is removed from public search while keeping existing applications.

For permanent deletion, use only this newly created disposable demo role and confirm on the app's page. Explain that deleting a job cascades to applications; closing it is the normal choice when history matters. Do not delete another person's records in a shared database.

## 6. Explain permissions

The automated tests show that candidates cannot post jobs and another employer cannot edit the first employer's job or read its applicants. A browser hiding a link is not sufficient; the server filters by ownership on every protected operation. Explain `403` for a forbidden role and `404` when an owned record cannot be found.

## Screenshot guide

Capture the home search results, candidate application dashboard and employer applicants page after running the steps. Use fictional accounts only; keep `.env` and real personal information out of view. Actual verification screenshots are in `screenshots/` when present. They show this local portfolio application, not a customer deployment.

## Two-minute explanation

"This is a personal Django portfolio project with MySQL. It has candidate and employer roles. Django renders HTML templates, and a small amount of JavaScript improves the forms. Users connect to profiles; employers own companies; companies have jobs; applications connect candidates to jobs. I can trace an application from a URL to a form, a permission check, a database insert and a redirect. Tests cover duplicate submissions and attempts to access another user's data. I used AI assistance and am learning the parts I can demonstrate. It is not deployed for real recruitment."

Only claim to have traced or tested a part after doing so yourself.
