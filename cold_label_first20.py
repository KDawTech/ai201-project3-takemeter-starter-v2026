#!/usr/bin/env python3
"""Independent first-20 labeling. Shows no AI-suggested labels."""
import csv
from pathlib import Path

PATH=Path(__file__).resolve().parent/'labels.csv'
CHOICES={'d':'debugging','i':'implementation','c':'conceptual'}

def save(rows):
    with PATH.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=['text','label','note']);w.writeheader();w.writerows(rows)

def main():
    with PATH.open('r',newline='',encoding='utf-8-sig') as f:
        rows=list(csv.DictReader(f))
    print('Cold labeling: 20 real posts, your independent judgment.')
    print('d=debugging, i=implementation, c=conceptual, q=quit')
    for idx in range(min(20,len(rows))):
        row=rows[idx]
        if row['label'] in CHOICES.values(): continue
        print('\n'+('='*74))
        print(f'POST {idx+1}/20 - read this entire post and choose one label')
        print('='*74+'\n'+row['text']+'\n')
        while True:
            choice=input('Label [d/i/c/q]: ').strip().lower()
            if choice=='q':
                print('Saved previous work.');return
            if choice in CHOICES:
                row['label']=CHOICES[choice]
                row['note']='cold'
                save(rows)
                break
            print('Choose d, i, c or q.')
    print('First 20 cold labels completed. Next run: python review_labels.py')

if __name__=='__main__':main()
