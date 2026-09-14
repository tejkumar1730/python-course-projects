"""Offline dictionary with spelling suggestions and a user word database."""
import argparse
import difflib
import json
from pathlib import Path

DATA = Path(__file__).with_name('words.json')

def lookup(word, words):
    word = word.strip().casefold()
    if not word:
        raise ValueError('Enter a word.')
    return words.get(word), difflib.get_close_matches(word, words, n=3, cutoff=0.6)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('word')
    parser.add_argument('--add', metavar='DEFINITION')
    parser.add_argument('--data', type=Path, default=DATA)
    args = parser.parse_args()
    try:
        words = json.loads(args.data.read_text(encoding='utf-8')) if args.data.exists() else {}
        if args.add is not None:
            if not args.word.strip() or not args.add.strip():
                raise ValueError('Word and definition cannot be blank.')
            words[args.word.strip().casefold()] = args.add.strip()
            args.data.parent.mkdir(parents=True, exist_ok=True)
            temp = args.data.with_suffix('.tmp')
            temp.write_text(json.dumps(words, indent=2, ensure_ascii=False), encoding='utf-8')
            temp.replace(args.data)
            print('Word saved.')
        else:
            definition, suggestions = lookup(args.word, words)
            print(definition or ('Not found. Suggestions: ' + ', '.join(suggestions) if suggestions else 'Not found. Add it with --add.'))
    except (ValueError, OSError) as error:
        parser.exit(1, f'Error: {error}\n')

if __name__ == '__main__':
    main()
