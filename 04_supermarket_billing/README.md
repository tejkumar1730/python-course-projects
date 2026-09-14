# Super Market Bill Generation System

Create an itemized receipt with line totals, percentage discount, tax on the discounted subtotal, and a unique receipt ID. Decimal arithmetic avoids floating point currency errors.

## Run

Requires Python 3.10+. From this folder:

```console
python app.py basket.json
python app.py basket.json --discount 10 --tax 5 --output generated/receipt.txt
```

## Behavior and limits

Basket format: a JSON list with name, positive integer quantity, and price as a decimal string. Price may be zero. Discount and tax range from 0 to 100; both default to zero. The sample tax is user-configured demonstration math, not a legal tax rule. Discounts and tax round half up to two decimal places.

## Learning topics

Input validation, functions, error handling, file/database operations, and separation of business logic from the command-line interface.
