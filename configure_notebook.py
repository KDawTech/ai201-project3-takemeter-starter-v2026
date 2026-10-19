#!/usr/bin/env python3
"""Patch the existing starter notebook's label map; keep a backup."""
from pathlib import Path
import json
import shutil

path=Path(__file__).resolve().parent / 'takemeter.ipynb'
if not path.exists():
    raise SystemExit('takemeter.ipynb not found. Run this in your actual GitHub repo.')
notebook=json.loads(path.read_text(encoding='utf-8'))
found=0
for cell in notebook.get('cells',[]):
    if cell.get('cell_type')!='code':
        continue
    s=''.join(cell.get('source',[]))
    old='LABELS = ["analysis", "hot_take", "reaction"]'
    new='LABELS = ["debugging", "implementation", "conceptual"]'
    if old in s:
        s=s.replace(old,new)
        cell['source']=s.splitlines(keepends=True)
        found+=1
    elif new in s:
        found+=1
if found!=1:
    raise SystemExit(f'Expected to replace one label map, found {found}; open notebook and change LABELS manually.')
backup=path.with_suffix('.ipynb.before_unit5.bak')
if not backup.exists():
    shutil.copy2(path,backup)
path.write_text(json.dumps(notebook,ensure_ascii=False,indent=1)+'\n',encoding='utf-8')
print('Notebook LABELS updated. Backup:',backup.name)
print('Open the notebook in VS Code, choose .venv, and run sections 1-5 only after labeling.')
