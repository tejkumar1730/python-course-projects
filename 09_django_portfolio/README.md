# Django Portfolio

Project cards are database-backed. Use the admin to add or edit projects; seed_demo adds the ten demo cards idempotently. The contact form validates and saves messages in the local admin inbox; no email is sent.

## Run

Use Python 3.10+ and an activated virtual environment. From this folder:

```console
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8009
```

Choose your own username and password when prompted. Open http://127.0.0.1:8009/ and use /admin/ for administration. No default credentials are included. Student management uses this staff login; portfolio pages are public.

## Test

```console
python manage.py test
python manage.py check
```

## Configuration

SQLite database defaults to db.sqlite3 and is excluded from Git. DJANGO_DB can point to another local database. The default development secret is random for each server process, so logins expire on restart. To keep sessions across restarts, set a private DJANGO_SECRET_KEY environment variable. DJANGO_DEBUG defaults to 1 for local development. With DJANGO_DEBUG=0 an explicit secret is required. Hosts are restricted to localhost, 127.0.0.1 and the Django test client.

This is a local course demonstration. Internet deployment needs production settings, HTTPS, a production application server, static-file hosting, access/rate-limit review and backups. See the [Django tutorial](https://docs.djangoproject.com/en/5.2/intro/tutorial01/) for framework background.
