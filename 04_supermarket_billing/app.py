"""Generate an itemized receipt from a JSON shopping basket."""
import argparse
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import json
from pathlib import Path
import uuid

def number(value):
    try: result=Decimal(str(value))
    except InvalidOperation as error: raise ValueError('Invalid numeric value.') from error
    if not result.is_finite(): raise ValueError('Numbers must be finite.')
    return result

def invoice(items, discount='0', tax='0'):
    discount,tax=number(discount),number(tax)
    if not 0<=discount<=100 or not 0<=tax<=100: raise ValueError('Percentages must be between 0 and 100.')
    if not isinstance(items,list) or not items: raise ValueError('Basket must be a non-empty list.')
    lines=[]; subtotal=Decimal(0)
    for item in items:
        name=str(item['name']).strip(); qty=item['quantity']; price=number(item['price'])
        if not name or type(qty) is not int or qty<=0 or price<0 or price*100!=(price*100).to_integral_value():
            raise ValueError('Items need a name, positive integer quantity and nonnegative price with up to two decimals.')
        total=price*qty; subtotal+=total
        lines.append(f'{name[:28]:28} {qty:>4} x {price:>9.2f} = {total:>10.2f}')
    reduction=(subtotal*discount/100).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
    taxes=((subtotal-reduction)*tax/100).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
    total=subtotal-reduction+taxes
    return '\n'.join(['SUPERMARKET | DEMO RECEIPT',f'Receipt: {uuid.uuid4().hex[:12]}',f'UTC: {datetime.now(timezone.utc).isoformat()}','Currency: INR','-'*64,*lines,'-'*64,f'Subtotal: {subtotal:.2f}',f'Discount ({discount}%): -{reduction:.2f}',f'Tax ({tax}%): {taxes:.2f}',f'TOTAL: INR {total:.2f}']),total

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('basket',type=Path); p.add_argument('--discount',default='0'); p.add_argument('--tax',default='0'); p.add_argument('--output',type=Path)
    args=p.parse_args()
    try:
        receipt,_=invoice(json.loads(args.basket.read_text(encoding='utf-8')),args.discount,args.tax)
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(receipt+'\n',encoding='utf-8')
        print(receipt)
    except (ValueError,KeyError,TypeError,OSError) as error: p.exit(1,f'Error: {error}\n')

if __name__=='__main__': main()
