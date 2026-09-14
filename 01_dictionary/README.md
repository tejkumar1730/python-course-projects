# Dictionary mini project

Offline lookup, case-insensitive matching, spelling suggestions, and adding/updating custom definitions. The bundled vocabulary is a 25-word programming glossary, not a general English dictionary.

## Run

Requires Python 3.10+. From this folder:

```console
python app.py python
python app.py pythn
python app.py "framework" --add "A reusable structure for building software."
python app.py framework
```

## Behavior and limits

Definitions live in words.json. --data PATH selects a separate JSON word file. Adding a definition replaces that word only. Invalid or blank inputs are rejected.

## Learning topics

Input validation, functions, error handling, file/database operations, and separation of business logic from the command-line interface.
