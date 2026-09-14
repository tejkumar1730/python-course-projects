# To-do list

Add tasks, filter/search pending tasks, mark done, reopen and delete. Priority 1 is highest. Optional ISO deadlines show overdue status. SQLite keeps tasks between runs.

## Run

Requires Python 3.10+. From this folder:

```console
python app.py add "Practice Django forms" --priority 1 --due 2030-01-01
python app.py list
python app.py list --search Django
python app.py done 1
python app.py list --all
python app.py reopen 1
python app.py delete 1
```

## Behavior and limits

Use the returned task ID. Dates use YYYY-MM-DD. --db PATH selects a different database and goes before the subcommand. Delete removes a local task permanently; there is no undo. Default database: tasks.sqlite3.

## Learning topics

Input validation, functions, error handling, file/database operations, and separation of business logic from the command-line interface.
