#!/usr/bin/env python3
"""Run TakeMeter Unit 5 notebook sections 1–5 from the command line.

This uses the original training code in takemeter.ipynb. No fake metrics.
Unreviewed AI labels are allowed only when explicitly acknowledged.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter
from pathlib import Path

LABELS = {'debugging', 'implementation', 'conceptual'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--allow-unreviewed', action='store_true',
                        help='Train on AI-suggested labels that have not been human-reviewed; disclosure still required.')
    args = parser.parse_args()

    repo = Path(__file__).resolve().parent
    os.chdir(repo)
    csv_path = repo / 'labels.csv'
    nb_path = repo / 'takemeter.ipynb'
    if not csv_path.exists() or not nb_path.exists():
        sys.exit('Missing labels.csv or takemeter.ipynb. Copy this file into your actual TakeMeter repo.')

    with csv_path.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != ['text', 'label', 'note']:
            sys.exit('labels.csv must contain text,label,note columns')
        rows = list(reader)

    if len(rows) < 150:
        sys.exit(f'Only {len(rows)} rows — not enough for the assignment stop rule.')
    if any(r['label'] not in LABELS or not r['text'].strip() for r in rows):
        sys.exit('Blank/invalid label or text remains. Finish the first 20 cold labels before training.')
    if any(r['note'].strip().lower() != 'cold' for r in rows[:20]):
        sys.exit('The first 20 posts must remain marked cold.')
    if len(set(r['text'] for r in rows)) != len(rows):
        sys.exit('Duplicate posts detected — inspect labels.csv for leakage risk.')

    counts = Counter(r['label'] for r in rows)
    print(f'Dataset: {len(rows)} rows; distribution: {dict(counts)}', flush=True)
    if max(counts.values()) / len(rows) > .70:
        sys.exit('A class exceeds the 70% assignment cap.')

    unreviewed = sum('review required' in r['note'].lower() for r in rows[20:])
    if unreviewed:
        print(f'WARNING: {unreviewed} AI-suggested rows are NOT human-reviewed.', flush=True)
        print('Do not claim they were reviewed in your README.', flush=True)
        if not args.allow_unreviewed:
            sys.exit('To proceed with provisional labels, add --allow-unreviewed')

    criteria = (repo / 'criteria.md')
    if criteria.exists() and 'AI DRAFT' in criteria.read_text(encoding='utf-8'):
        print('WARNING: criteria.md is still an AI draft. Review/adopt or revise its five targets before submitting.', flush=True)

    notebook = json.loads(nb_path.read_text(encoding='utf-8'))
    ns = {'__name__': '__main__'}
    unit5_cells = []
    for idx, cell in enumerate(notebook['cells']):
        src = ''.join(cell.get('source', []))
        if cell.get('cell_type') == 'markdown' and 'Unit 6 starts here' in src:
            break
        if cell.get('cell_type') == 'code' and src.strip():
            if src.lstrip().startswith('!') or '\n%' in src:
                sys.exit(f'Cell {idx} has notebook-specific syntax. Run it in VS Code instead.')
            unit5_cells.append((idx, src))

    if not unit5_cells:
        sys.exit('No notebook training cells found.')

    print(f'Running {len(unit5_cells)} existing Unit 5 notebook code cells.', flush=True)
    print('The first download and model training may take several minutes.', flush=True)

    for idx, src in unit5_cells:
        print(f'\n===== notebook cell {idx} =====', flush=True)
        exec(compile(src, f'{nb_path.name}:cell_{idx}', 'exec'), ns)

    created = [name for name in ('results.json', 'test_split.csv') if (repo / name).exists()]
    print('\nOutput files: ' + (', '.join(created) if created else 'none'), flush=True)
    if len(created) != 2:
        sys.exit('Training ran but did not create both expected output files. Check error/output above.')
    print('Training complete. Run: python apply_unit5_readme.py', flush=True)

if __name__ == '__main__':
    main()
