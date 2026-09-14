# Exploratory Data Analysis

A reproducible CSV explorer that reports row count, duplicate rows, missing cells, distinct values, numeric statistics, and frequent categories. Produces JSON and a readable HTML report using only the standard library.

## Run

Requires Python 3.10+. From this folder:

```console
python app.py sample_sales.csv --output generated/eda
# Open generated/eda/report.html
python app.py path/to/your.csv --output generated/my-report
```

## Behavior and limits

The included 12-row sales dataset is synthetic, authored for this project. It deliberately includes one duplicate row, one missing region and one missing quantity. Quantity median is 4 across 11 present observations, retaining duplicates. Blank/whitespace cells count as missing. Every nonblank value must parse as finite numeric data for a column to be summarized numerically; otherwise it is categorical. No imputation, deletion, causal claims or business recommendations are made. Numeric IDs may be inferred as numbers; interpret their summaries as identifiers, not measures. Standard deviation uses the sample formula and is null for one observation. This lightweight program reads the CSV into memory and is intended for small learning datasets.

## Learning topics

Input validation, functions, error handling, file/database operations, and separation of business logic from the command-line interface.
