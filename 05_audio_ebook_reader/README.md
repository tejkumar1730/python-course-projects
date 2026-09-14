# Audio e-book reader

A Python local server with a browser reader for TXT ebooks and pasted text. Voice selection, reading speed, pause/resume, stop, chunked playback and progress are included.

## Run

Requires Python 3.10+. From this folder:

```console
python app.py
# Open http://127.0.0.1:8005 in Chrome or Edge
python app.py --port 8015
```

## Behavior and limits

Load a UTF-8 .txt file under 2 MB or paste text, select a voice, and click Read aloud. PDF/EPUB import and audio-file export are not implemented. Speech uses browser Web Speech support; voices and offline availability depend on the device. Voices marked local use installed speech; other voices may use an online service. Changes to voice/speed apply to the next chunk. Ctrl+C stops the local server.

## Learning topics

Input validation, functions, error handling, file/database operations, and separation of business logic from the command-line interface.
