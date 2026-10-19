#!/usr/bin/env python3
"""Validate your finished TakeMeter labels before you train; never fills labels."""
from pathlib import Path
from collections import Counter
import csv
p=Path(__file__).resolve().parent/'labels.csv'
with p.open('r',encoding='utf-8-sig',newline='') as f:
    reader=csv.DictReader(f)
    if reader.fieldnames != ['text','label','note']:
        raise SystemExit(f'Wrong columns: {reader.fieldnames}')
    rows=list(reader)
labels={'debugging','implementation','conceptual'}
errors=[]
if len(rows)<200:errors.append(f'Only {len(rows)} rows (goal 200)')
for i,r in enumerate(rows,1):
    if not r['text'].strip():errors.append(f'Row {i} empty text')
    if r['label'] not in labels: errors.append(f'Row {i} blank/invalid label: {r["label"]!r}')
    if i<=20 and r['note'].strip().lower()!='cold':errors.append(f'Row {i}: first 20 must be cold')
    if i>20 and 'review required' in r['note'].lower():errors.append(f'Row {i} AI label has not yet been personally reviewed')
counts=Counter(r['label'] for r in rows if r['label'] in labels)
print(f'Total: {len(rows)}; unique text: {len(set(r["text"] for r in rows))}')
for label in sorted(labels):
    n=counts[label]
    print(f'  {label}: {n} ({n/len(rows):.1%})')
    if n/len(rows)>.70:errors.append(f'{label} exceeds 70%')
if len(set(r['text'] for r in rows))!=len(rows):errors.append('Duplicate text')
if errors:
    print('\nNOT READY FOR TRAINING')
    for e in errors[:25]:print(' -',e)
    if len(errors)>25:print(f'...plus {len(errors)-25} more review items')
    raise SystemExit(1)
print('\nREADY FOR TRAINING: labels complete, reviewed, balanced, and nonduplicated')
