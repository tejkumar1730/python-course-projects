# Understand and explain the Job Portal

This guide describes the code in this directory. It is not a script for claiming prior experience. The implementation was created with AI assistance on 27 September 2026. Read the source, run the demo and make a small change before saying you understand it.

## Architecture

```text
Browser: HTML forms + CSS + a little JavaScript
  -> HTTP request
  -> Django URL routing and middleware (sessions, authentication, CSRF)
  -> view + role/ownership check + form validation
  -> Django ORM -> MySQL tables
  -> rendered HTML, or redirect after a successful POST
```

This is Django's model-template-view pattern. Models describe data; views handle requests; templates produce HTML. There is one business app, `jobs`, to keep the flow easy to follow. There is no separate frontend framework or REST API here. The Product API project demonstrates that other approach separately.

## Database schema and relationships

| Table/model | Main fields | Relationship/rule |
|---|---|---|
| Django User (`auth_user`) | id, username, hashed password, email, first_name | Built-in authentication; username unique |
| Profile (`jobs_profile`) | id, user_id, role | One profile per user; candidate or employer in normal registration |
| Company (`jobs_company`) | id, owner_id, name, location, website, description | One company per employer |
| Job (`jobs_job`) | id, company_id, title, location, employment_type, description, requirements, salary_min/max, closing_date, is_active, created_at | A company has many jobs; salary maximum cannot be below minimum when both exist |
| Application (`jobs_application`) | id, job_id, candidate_id, cover_letter, status, applied_at | Connects a user to a job; unique pair `(job_id, candidate_id)` |

```text
User 1---1 Profile
User 1---1 Company 1---many Job 1---many Application
User (candidate) 1----------------many Application
```

Foreign keys use cascade deletion. Removing a company deletes its jobs; removing a job deletes its applications. This simple portfolio choice is documented and confirmed in the UI. Closing a job preserves application history. Candidate/employer role rules are enforced by application code; a trusted database administrator could bypass them.

## Main files and why they exist

- `manage.py` runs Django commands; it is not the business logic.
- `config/settings.py` reads environment settings, chooses MySQL/explicit SQLite and installs middleware.
- `config/urls.py` connects auth/admin routes and the business URL module.
- `jobs/urls.py` maps friendly paths and names to view functions.
- `jobs/models.py` declares the four business models, choices, relations and constraints.
- `jobs/forms.py` exposes only permitted input fields. Registration inherits Django's password validation and creates a profile/company in one transaction.
- `jobs/permissions.py` checks login and role. It does not replace ownership checks.
- `jobs/views.py` handles requests, selects owned objects, saves forms and chooses responses.
- `templates/` renders escaped HTML; forms include CSRF tokens.
- `static/jobs/app.js` toggles company input and counts cover-letter characters. The server still validates.
- `jobs/migrations/0001_initial.py` creates the schema. `seed_demo.py` creates rows; these are different operations.
- `jobs/tests.py` demonstrates expected behavior, including forbidden actions and seed repeatability.

## Trace one request: applying for a job

1. The browser requests `/jobs/2/apply/` using GET.
2. `jobs/urls.py` routes it to `apply` in `views.py`.
3. `role_required(CANDIDATE)` requires a logged-in candidate. Django's session identifies the user.
4. The view loads the job, checks that it is active and not expired, and checks whether an application already exists.
5. GET renders the cover-letter form. No row is created yet.
6. POST submits the cover letter and CSRF token. Django's middleware checks CSRF; the form requires 30-3000 characters.
7. `form.save(commit=False)` builds an unsaved Application object. The server sets `job` and `candidate` from trusted context. Status defaults to Submitted.
8. `transaction.atomic()` saves the row. The unique constraint also rejects two near-simultaneous duplicate requests. The view handles an integrity error as an already-applied message.
9. The server redirects to the dashboard. That separate GET lists only the current user's applications.

The redirect prevents a normal page refresh from resubmitting the form. The database constraint is still required because redirects and frontend controls alone do not prevent duplicate requests.

## CRUD mapping

| Operation | URL/view | Server behavior |
|---|---|---|
| Create job | `/jobs/new/`, `job_create` | Employer-only; company assigned from logged-in owner |
| Read jobs | `/`, `job_list`; `/jobs/<id>/`, `job_detail` | Search active, nonexpired roles; private access rules for closed roles |
| Update job | `/jobs/<id>/edit/`, `job_edit` | Query includes `company__owner=request.user`; validate form |
| Delete job | `/jobs/<id>/delete/`, `job_delete` | GET shows confirmation; POST deletes owned job and applications |
| Update company | `/company/edit/`, `company_edit` | Owner chosen on server; posted owner IDs ignored |
| Create application | `/jobs/<id>/apply/`, `apply` | Candidate-only; unique application per candidate/job |
| Read applications | `/dashboard/` or `/jobs/<id>/applicants/` | Own candidate applications or applicants for owned employer jobs |
| Update status | `/applications/<id>/status/`, `application_status` | POST-only, job owner only, allowed status choices only |

No candidate withdrawal or cover-letter editing is implemented. Do not claim every table has a full public CRUD interface.

## Authentication, authorization and validation

**Authentication:** Django's User model and built-in login views verify hashed passwords. Sessions link a browser cookie to server-side session data. Logout is POST. Passwords are created through Django APIs, not stored as plaintext.

**Authorization:** a role decorator restricts employer/candidate operations. Ownership filters independently restrict which employer's jobs/applicants can be read or changed. Forging company/candidate/status fields in a request does not grant access because the forms do not expose those assignments.

**Validation:** Django forms check required fields, lengths, email/URL format, role choices, password strength, closing dates and cover letters. `Job.clean()` checks salary ordering. Database constraints enforce salary ordering and unique applications even if a prior application check becomes stale. Django model `save()` does not automatically run `full_clean()`; normal web writes go through validated ModelForms.

**CSRF and escaping:** POST forms carry a token so another site cannot silently submit a request with the user's session. Templates escape untrusted text to reduce script injection. Neither replaces authentication or permission checks.

## Common bugs and how to investigate

| Symptom | Likely cause | What to inspect |
|---|---|---|
| A candidate sees an employer-only operation | Only the UI was checked | Role decorator on the view |
| Another employer can edit a job | Object loaded by ID without owner filter | `get_object_or_404(..., company__owner=request.user)` |
| Duplicate applications | Only an `exists()` check was used | Unique DB constraint and atomic error handling |
| Salary range accepted incorrectly | Cross-field rule missing | `Job.clean()` plus DB check |
| New user has no Profile | Related rows saved separately | Registration's atomic transaction |
| 403 on valid POST | Missing/expired CSRF token | Template token, cookies and request origin |
| No tables or old schema | Migration not applied to current database | Database env and `showmigrations` |
| Jobs disappear over time | Closing date passed | `accepting_applications` and search filters |
| Page refresh repeats a write | Rendering directly after POST | Redirect-after-success behavior |
| Employer profile created manually has no company | Admin bypassed registration invariant | Add the linked company or use normal registration |

## Likely interview questions

1. **Why Django?** It supplies routing, forms, ORM, authentication and templates, so I can concentrate on the portal workflow. I chose a small conventional design to understand the request flow.
2. **Why MySQL?** Users, companies, jobs and applications have clear relational links. I wanted to practise foreign keys, constraints and persistent data. I did not benchmark it against other databases.
3. **Why a separate Profile?** It adds a portal role while keeping Django's built-in User. One-to-one means at most one profile per user. A custom User could be considered at the start of a larger project.
4. **Can a candidate become an admin through registration?** No. The registration form accepts only candidate/employer and does not expose `is_staff` or `is_superuser`.
5. **Why use both role and ownership checks?** Role answers what type of operation is allowed; ownership answers which specific records the user can access.
6. **How does job search work?** GET parameters feed ORM `icontains` filters combined with `Q` conditions. Only active, nonexpired jobs are listed, and a paginator limits each page.
7. **What does `select_related` do?** It retrieves foreign-key-related objects in the same query, avoiding a new query for each job's company or application's job in a loop. It is not a cache of the whole database.
8. **Why `save(commit=False)`?** It creates an unsaved model from valid input so the server can assign trusted ownership before saving.
9. **How do you stop duplicate applications?** An early existence check gives a clear message, and a unique constraint on job/candidate handles races. A transaction keeps database error handling clean.
10. **What is the difference between closing and deleting a job?** Closing changes `is_active` and preserves history. Deleting removes the job and cascades to applications. The UI explicitly confirms deletion.
11. **Does JavaScript protect the database?** No. It improves form usability; all important validation is repeated on the server.
12. **Why return 404 for another employer's record?** The owned-object query cannot find it within that employer's allowed records. It also avoids revealing details about another employer's data.
13. **What did you test?** Twenty cases cover the core flows, invalid input, roles, owner isolation, CSRF, escaped content and repeatable seeding on both MySQL and SQLite. I still need to distinguish tests I personally ran from the assistant's verification record.
14. **Is it production-ready?** No. It uses local development hosting and fictional data. Email workflows, abuse prevention, deployment hardening, backups, accessibility audits and scale testing remain future work.
15. **What would you change next?** Pick one achievable feature, such as application withdrawal, and explain the model/view/permission/test changes before claiming to have implemented it.
16. **Did you write all this unaided?** No. The initial implementation and notes used AI assistance. Explain which files you have reviewed, changes you made and behavior you can demonstrate. Do not invent months of work or commercial users.

## A small exercise before the interview

Add a new employment-type choice such as Contract, generate its migration, update a demo job, and add a test that filters by the new choice. Explain why a model choice, migration and user interface must stay consistent. Record only work you actually complete in your practice log.
