# Product API interview preparation

This project is portfolio work being completed in September 2026 with AI assistance. Read the code, run the tests, make small changes yourself and explain only what you have practiced. Do not claim this was a company system, a deployed client project, earlier work or a project built entirely without assistance.

## A 60-second explanation

"I am building a small product management API using Python, Django REST Framework and MySQL as a portfolio project. An authenticated user can create, read, update and delete their own products. Each product has a unique SKU, name, description, price and stock. I use a serializer to validate request data, a model to define storage, and a viewset to handle CRUD. The queryset is filtered by the authenticated user, so one user's products are not visible to another. I also added automated tests for validation, CRUD and access restrictions. I used AI assistance, and I am learning it by running, inspecting and modifying the code."

Adapt that explanation to what you have personally completed. If MySQL has not been run on your machine yet, say you have used SQLite for the current local demonstration and still need to verify MySQL yourself.

## Architecture

```text
API client / DRF browser page
       |
       | HTTP + JSON, token or session cookie
       v
Django URL router
       v
Authentication -> IsAuthenticated permission
       v
ProductViewSet: owner-filtered queryset
       v
ProductSerializer: parse, validate, represent JSON
       v
Product model -> Django ORM -> MySQL tables
```

These are logical responsibilities; not every method calls them in exactly this sequence. For example, a detail update first looks up the owner-filtered object, then validates the input. Search and pagination operate on the filtered queryset.

| File | What to explain |
| --- | --- |
| `manage.py` | Entry point for migrate, seed, test and runserver commands. |
| `config/settings.py` | Installed apps, MySQL/environment settings, authentication, page size. |
| `config/urls.py` | Router maps product URLs to the viewset; token and browser login URLs. |
| `products/models.py` | Fields, owner relationship, ordering, uniqueness and database checks. |
| `products/serializers.py` | Maps model fields to JSON; read-only output fields and input rules. |
| `products/views.py` | CRUD viewset, owner filter, logged-in owner assignment and duplicate race handling. |
| `products/admin.py` | Convenient trusted-staff interface, distinct from the owner-restricted API. |
| `products/migrations/0001_initial.py` | Database schema change stored with source code. |
| `products/management/commands/seed_demo.py` | Creates a demo account and repeatable products within a transaction. |
| `products/tests/test_api.py` | Requests the API and checks response codes plus saved database state. |

## Database schema

| `products_product` column | Meaning and rule |
| --- | --- |
| `id` | Automatic integer primary key. |
| `owner_id` | Foreign key to Django's `auth_user`; one user has many products. |
| `sku` | Globally unique identifier, max 32 characters. API accepts uppercase letters/digits/hyphens/underscores. |
| `name` | Max 120 characters; API rejects blank and whitespace-only input. |
| `description` | Optional text, max 2000 characters in API/model validation. |
| `price` | Decimal(10,2), zero or positive; database CHECK as well as validation. |
| `stock` | Nonnegative integer; API upper bound 2147483647 is portable across the supported databases. |
| `created_at`, `updated_at` | Django-managed timestamps; API clients cannot set them. |

Django also maintains user, permission, admin, session, migration and token tables. `authtoken_token` associates a token with a user. Passwords are stored as hashes through Django's password methods. Tokens are bearer secrets stored by the standard DRF token implementation; never share them.

The `owner_id` foreign key and unique SKU have database indexes. No extra indexes are necessary for this small sample. Default text search uses containment and should not be described as a full-text search engine. Deleting a user through Django cascades to their products. Do not claim business audit retention exists.

Validation is not identical at every layer: API serializers reject blank names and invalid formats, while the database guarantees key relationships, unique SKU and nonnegative price/stock. Calling `Product.objects.create()` directly does not call `full_clean()` automatically; code outside the serializer must validate appropriately. `TextField(max_length=2000)` is a validation limit, not a universal database text-length constraint.

## Trace one POST request

For `POST /api/products/` with JSON and a token:

1. The router selects `ProductViewSet.create()` supplied by DRF.
2. Token authentication identifies the user; `IsAuthenticated` rejects an anonymous request.
3. `ProductSerializer` checks required fields, types, precision, ranges, format and SKU uniqueness.
4. `perform_create()` calls `save_product()` with `owner=request.user`. A client cannot choose another owner.
5. A transaction saves the product through Django's ORM. MySQL enforces its constraints too.
6. The serializer creates the JSON response and DRF returns 201.

A duplicate normally fails validation before saving. If two simultaneous requests both pass that check, the unique database index decides which one succeeds. The save helper catches that integrity error and returns a `sku` validation error if a duplicate now exists. Other unexpected integrity errors are re-raised rather than mislabeled as duplicates.

For GET detail, DRF searches the owner-filtered queryset by id and returns 404 when no accessible row matches. For PATCH it first finds that same accessible row, then validates only supplied fields. For DELETE it finds and deletes the accessible row, returning an empty 204 response.

## CRUD, authentication and validation

| Topic | What this code actually does |
| --- | --- |
| Create | POST inserts a product owned by `request.user`. |
| Read | GET list/detail reveals only the current user's products. |
| Update | PUT requires required writable fields; PATCH allows partial changes. Omitted optional fields remain unchanged on update. |
| Delete | DELETE removes the product permanently. There is no soft delete. |
| Authentication | Token login checks username/password; clients send `Authorization: Token ...`. Browser login uses Django sessions. |
| Authorization | The default permission requires authentication; the queryset restricts ownership. |
| Validation | Serializer/model-derived validators check values before save; database constraints protect core storage invariants. |
| Errors | 400 invalid input/credentials, 401 missing or invalid token, 403 possible session CSRF failure, 404 missing or inaccessible product, 429 token-login throttle. |

Token authentication appears before session authentication, so anonymous API requests receive 401. Session-authenticated browser writes require CSRF protection. Using tokens avoids session CSRF requirements, but tokens still require secure storage and HTTPS outside localhost. CORS and CSRF are different concepts; this project does not include a separate cross-origin frontend.

## Likely interview questions and honest answers

1. **Why Django REST Framework?** It provides serializers, authentication, routing, pagination and reusable CRUD views. I used those components instead of writing those mechanisms myself.

2. **What does a serializer do?** It converts model instances into response-friendly data and checks incoming request data before creating or updating a model. Here the serializer is a `ModelSerializer`, so many rules come from the model fields.

3. **What is a viewset?** It groups related API actions in one class. `ModelViewSet` supplies list, retrieve, create, update, partial update and destroy; the router maps HTTP methods and URLs to those actions.

4. **Authentication versus authorization?** Authentication establishes who is making the request. Authorization decides which data they can access. A valid token is not enough to access another user's product because the queryset filters by owner.

5. **Why filter the queryset instead of only checking object permissions?** The queryset protects list responses as well as individual lookups. An object permission alone does not automatically filter every row in a list response. [DRF permissions reference](https://www.django-rest-framework.org/api-guide/permissions/)

6. **Why return 404 for another user's product?** That product is outside this user's accessible queryset. This also avoids confirming the existence of someone else's record through the detail endpoint. SKU uniqueness is global, so a conflicting SKU can still yield a validation error; this is an explicit small-project design choice.

7. **Why Decimal instead of float?** Prices need fixed decimal precision. Binary floating-point can represent some decimal values approximately. A Decimal field with two decimal places provides predictable stored amounts for this scope.

8. **Where do you stop duplicate SKUs?** Serializer validation gives a readable 400 error; a database unique index prevents duplicates even during competing requests. The transaction error handler translates a duplicate race to the same type of client error.

9. **PUT versus PATCH?** PUT sends all required writable fields; PATCH sends only changed fields. In this implementation omitted optional fields remain unchanged on update, so I explain that behavior rather than claiming a strict replace-every-field implementation.

10. **What is a migration?** A version-controlled description of database schema changes. `makemigrations` generates it from model changes; `migrate` applies pending migrations to the selected database.

11. **Does your ORM prevent SQL injection?** Normal Django ORM queries pass values separately from SQL syntax. I use ORM filters here and do not concatenate user input into raw SQL. That does not mean all possible application code is automatically secure.

12. **How did you test it?** The test client sends requests against a test database. Tests verify saved values, error status codes, no unauthorized access, duplicate/negative/blank rejection, pagination and seeding. I can run the suite and explain one test line by line. Say which database you actually ran it against.

13. **How does pagination help?** It limits rows returned in one response and makes result size manageable. This API uses ten rows per page and includes the total count and next/previous links. It does not solve every large-dataset performance problem.

14. **What does `select_related("owner")` do?** It joins the user when fetching products, avoiding a separate user query per product when the serializer outputs the owner's username.

15. **Are the tokens JWTs?** No. They are standard DRF database-backed tokens. They do not expire automatically. The project is simpler to explain this way, but a real deployment needs a defined expiration/revocation policy.

16. **Does logging out revoke the token?** Browser logout ends a session only. An administrator can delete the DRF token to revoke API access for that token. Password changes alone do not revoke existing tokens in this implementation.

17. **Can two users update stock safely as an inventory system?** Product ownership already limits who can update a row, but simultaneous requests from one account still use last-write-wins. This API edits a count; it does not implement reservations or stock movements. An ordering system would require atomic updates/locking and additional business rules.

18. **What would you improve next?** After understanding this version, I would add categories, API schema documentation and a deliberate deployment/security design. For real stock tracking, I would add stock movement records and atomic stock adjustments.

19. **What was your contribution if you used AI?** I used AI to help generate an initial implementation and explanations. My contribution is the work I can demonstrate: setup, testing, inspecting each part, identifying behavior and making changes. I do not claim to have independently written sections I have not yet understood.

20. **Was this used by real users or deployed?** No production usage or deployment is claimed. It is a local portfolio project being completed now before the interview. If I later deploy it, I will describe the actual deployment and date.

## Bugs worth understanding

| Bug or symptom | Cause and correction |
| --- | --- |
| Every user's products appear in list | An unrestricted `Product.objects.all()` was used. Filter by `request.user` before search/pagination. |
| User can assign a different owner | Owner was writable or trusted from JSON. Keep it read-only and assign it server-side. |
| 500 from duplicate requests | Serializer checks alone cannot prevent races. Add a unique DB constraint and handle that specific conflict. |
| Negative price saved from a script | `save()` does not automatically call every model validator. Validate non-API writes and keep database CHECK constraints. |
| Browser POST gets 403 | A session request lacks a valid CSRF token. Use the browser form or a correctly authenticated token request. |
| A valid token stops working after switching databases | The user/token data live in the selected database; obtain a token there. |
| Price looks like a JSON string | DRF represents Decimal values as strings by default to preserve decimal precision. |
| Seed resets demonstration edits | The command intentionally restores its three sample rows; it is for local sample data. |

## Practice before the interview

1. Start from a new local database, migrate and seed it yourself.
2. Create one product, change its stock and delete it using an API client.
3. Run the automated suite on MySQL and explain an ownership test.
4. Change the pagination size to five, observe the response, then restore it.
5. Add a temporary validation rule yourself, observe its 400 response and remove it.
6. Explain POST from URL to database without reading these notes.
7. If you cannot answer a detail, say: "I have not implemented or studied that part yet. In this project, the current behavior is ..." Then show the behavior you do understand.

An accurate resume line after completing and verifying the work: **Built a portfolio product CRUD API with Django REST Framework and MySQL, including token authentication, owner-based access, validation, pagination and automated API tests.** Do not turn this into a claim of employment, production scale or independent authorship.
