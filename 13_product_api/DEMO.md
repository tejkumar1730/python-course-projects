# Five-minute Product API demonstration

Complete README setup and start Django on port 8002. These are instructions to produce a real demonstration, not a claim that a demonstration was recorded. Use the local sample account and avoid showing `.env`, database passwords or token responses on screen.

## 1. Explain the scope (30 seconds)

"This is a portfolio API I am completing for interview preparation. It lets a signed-in user manage their own products. I used Django REST Framework for routing, JSON validation and authentication, and MySQL for persistence. I used AI assistance and then ran the project, reviewed the code and tested the behaviors I can explain."

Only use the final sentence after doing those activities yourself. For the database claim, show MySQL running and explain the configured backend. If you used the optional SQLite mode, say that directly.

## 2. Read the seeded products (45 seconds)

1. Open <http://127.0.0.1:8002/api/products/>. Before logging in, the response should be 401.
2. Click **Log in**, use `tej_demo` with the password you chose during seeding, then return to the product list.
3. Show the response's `count` and `results`; explain that there are three seeded products and pages contain up to ten rows.
4. Visit `?search=mouse` and then `?ordering=price` to show server-side search and ordering.

Suggested screenshot: the logged-in product list or search result, with the URL and HTTP 200 visible. The browser session avoids exposing a token in the screenshot.

## 3. Create, read, update and delete (90 seconds)

Use the browsable API's HTML form or JSON input for POST:

```json
{
  "sku": "LIVE-DEMO-01",
  "name": "Interview Notebook",
  "description": "Created during the live portfolio walkthrough",
  "price": "149.50",
  "stock": 8
}
```

Expect 201. Copy the returned `id` and visit `/api/products/THAT_ID/`. To make a partial update reliably, use the PowerShell or curl PATCH example in README with `{"stock":7}`. Expect 200 with the same name and new stock. The detail page also supports PUT, which needs every required writable field, and DELETE. Delete this demonstration product and show that a later GET returns 404.

Suggested screenshots: the POST 201 response and the successful detail response after the stock update. The screenshot must reflect the actual run, not invented sample output.

## 4. Demonstrate validation and ownership (90 seconds)

1. Submit another POST using `DEMO-MOUSE`. Expect 400 with an error under `sku`.
2. Use a new SKU but set `price` to `-1.00`, `stock` to `-1` or `name` to spaces. Expect 400; no row is inserted.
3. Create a second user through `manage.py createsuperuser` using a different username, or create an ordinary account through Django admin. Log in as that account.
4. That user's product list is empty initially. Visiting the first user's product id returns 404.
5. Explain that `get_queryset()` adds `owner=request.user`, so ownership applies to read, update and delete as well as list. Being an admin account does not bypass this API filter; the separate Django admin interface is privileged.

Suggested screenshot: field validation errors or the second account's empty list. Do not include account creation passwords.

## 5. Show code and tests (45 seconds)

Open `products/models.py`, `serializers.py` and `views.py` in that order. Describe one field, one validation rule and the ownership filter. Run `python manage.py test` using the project's virtual environment and show the summary. Read the result from your own run; do not repeat a test count or backend claim that you have not verified.

## Cleanup and repetition

- Delete `LIVE-DEMO-01` if the demo stopped before deletion.
- `python manage.py seed_demo` restores only the three sample product rows for the existing demo user. It preserves the password and does not clear all data.
- Browser logout ends the session. API tokens remain valid until removed in Django admin; do not record or publish them.
- If taking screenshots, save them in an optional `screenshots/` directory and caption each with the actual action/backend shown. Do not add secrets or real personal information.
