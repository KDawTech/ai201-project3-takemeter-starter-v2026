#!/usr/bin/env python3
"""Review every AI-suggested row individually, using complete post text."""
import csv
from pathlib import Path

PATH=Path(__file__).resolve().parent/'labels.csv'
CHOICES={'d':'debugging','i':'implementation','c':'conceptual'}
REVIEWED='AI pre-labeled; reviewed and corrected'


def save(rows):
    with PATH.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=['text','label','note']);w.writeheader();w.writerows(rows)

def main():
    with PATH.open('r',newline='',encoding='utf-8-sig') as f:
        rows=list(csv.DictReader(f))
    print('Review all 200 AI-suggested labels. Full post shown before approval.')
    print('Enter=accept suggestion, d=debugging, i=implementation, c=conceptual, q=quit')
    for idx in range(20,len(rows)):
        row=rows[idx]
        if 'review required' not in row['note'].lower(): continue
        print('\n'+('='*74))
        print(f'POST {idx+1}/{len(rows)}, AI suggestion: {row["label"]}')
        print('='*74+'\n'+row['text']+'\n')
        while True:
            answer=input('Accept Enter / change [d/i/c] / quit q: ').strip().lower()
            if answer=='q':
                print('Saved previous reviews.');return
            if answer=='' or answer in CHOICES:
                if answer in CHOICES: row['label']=CHOICES[answer]
                row['note']=REVIEWED
                save(rows)
                break
            print('Enter, d, i, c, or q.')
    print('Review finished. Run python check_labels.py')

if __name__=='__main__':main()
