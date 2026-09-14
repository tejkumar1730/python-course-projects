# Railway Tickets Reservation System

Search demo trains, see date-specific capacity, reserve multiple seats, retrieve a ticket by PNR, and cancel a booking. SQLite transactions prevent overselling.

## Run

Requires Python 3.10+. From this folder:

```console
python app.py search 2030-01-01
python app.py search 2030-01-01 --origin Hyderabad
python app.py book 101 2030-01-01 "Demo Passenger" --seats 2
python app.py ticket YOUR_PNR
python app.py cancel YOUR_PNR
```

## Behavior and limits

Use today or a future date. Copy YOUR_PNR from the booking result. Fares and routes are fictional demo data; no real ticket is issued. Data persists in railway.sqlite3; --db PATH must precede the subcommand. Cancellation restores capacity and cannot be repeated.

## Learning topics

Input validation, functions, error handling, file/database operations, and separation of business logic from the command-line interface.
