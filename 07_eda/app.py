"""Explore a CSV: missing values, duplicates, numeric summaries and categories."""
import argparse
from collections import Counter
import csv
import html
import json
import math
from pathlib import Path
import statistics

def analyze(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as stream:
        reader=csv.reader(stream); headers=next(reader,None)
        if not headers or any(not x.strip() for x in headers) or len(set(headers))!=len(headers):
            raise ValueError('CSV must have nonempty, unique column names.')
        rows=list(reader)
    if not rows: raise ValueError('CSV contains no data rows.')
    if any(len(row)!=len(headers) for row in rows): raise ValueError('Every row must match the header width.')
    result={'source':Path(path).name,'rows':len(rows),'duplicate_rows':len(rows)-len(set(tuple(x) for x in rows)),'columns':{}}
    for index,name in enumerate(headers):
        values=[row[index].strip() for row in rows]; present=[v for v in values if v]
        info={'missing':len(values)-len(present),'distinct':len(set(present))}
        numeric=[]
        for value in present:
            try: number=float(value)
            except ValueError: break
            if not math.isfinite(number): break
            numeric.append(number)
        if present and len(numeric)==len(present):
            info.update(type='numeric',count=len(numeric),minimum=min(numeric),maximum=max(numeric),mean=statistics.mean(numeric),median=statistics.median(numeric),sample_stddev=statistics.stdev(numeric) if len(numeric)>1 else None)
        else:
            info.update(type='categorical',top_values=Counter(present).most_common(5))
        result['columns'][name]=info
    return result

def report(data):
    cards=[]
    for name,info in data['columns'].items():
        rows=''.join(f'<tr><th>{html.escape(str(k))}</th><td>{html.escape(str(v))}</td></tr>' for k,v in info.items())
        cards.append(f'<section><h2>{html.escape(name)}</h2><table>{rows}</table></section>')
    return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CSV exploration</title><style>body{font:16px/1.6 system-ui;background:#f4f6fa;color:#17233c;max-width:1000px;margin:auto;padding:32px}h1{font-size:40px}section{background:white;border:1px solid #dbe2ee;border-radius:12px;padding:20px;margin:20px 0}table{border-collapse:collapse;width:100%}td,th{text-align:left;border-bottom:1px solid #eee;padding:8px;overflow-wrap:anywhere}</style><h1>CSV exploration</h1>'+f'<p>Source: {html.escape(data["source"])} · {data["rows"]} rows · {data["duplicate_rows"]} duplicate rows</p><p>Descriptive results only. Blank cells count as missing; duplicate rows are reported and retained. Numeric inference requires every nonblank cell to be a finite number. No values are imputed or removed.</p>'+''.join(cards)+'</html>'

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('csv',type=Path); p.add_argument('--output',type=Path,default=Path('generated/eda'))
    args=p.parse_args()
    try:
        data=analyze(args.csv); args.output.mkdir(parents=True,exist_ok=True)
        (args.output/'summary.json').write_text(json.dumps(data,indent=2,allow_nan=False),encoding='utf-8')
        (args.output/'report.html').write_text(report(data),encoding='utf-8')
        print(json.dumps(data,indent=2)); print(f'Report: {args.output / "report.html"}')
    except (OSError,ValueError,csv.Error) as error: p.exit(1,f'Error: {error}\n')

if __name__=='__main__': main()
