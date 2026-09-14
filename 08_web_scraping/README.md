# Web Scraping

Parse HTML into a page title, h1/h2/h3 headings and deduplicated HTTP(S) links. Nested link text and relative URLs are supported. Output can be saved as JSON.

## Run

Requires Python 3.10+. From this folder:

```console
python app.py --file sample.html
python app.py --file sample.html --base https://example.com/ --output generated/links.json
python app.py --url https://YOUR-PERMITTED-SITE.example/page --output generated/page.json
```

## Behavior and limits

The local sample works offline and is the verified demonstration. Replace the placeholder URL with a public page you are allowed to scrape. Live mode requires readable robots.txt permitting the URL, rejects redirects, has a 10-second timeout and a 2 MB page limit. It fetches one page, not a crawl, and does not execute JavaScript. Login-protected pages and missing/unreadable robots.txt are intentionally unsupported. Website terms and HTML structure vary; live extraction is not guaranteed. Output ignores javascript: and other non-web links.

## Learning topics

Input validation, functions, error handling, file/database operations, and separation of business logic from the command-line interface.
