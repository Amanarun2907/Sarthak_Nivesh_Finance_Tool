# coding: utf-8
import json


# Load all parts
all_cells = []
for part in ['nb_cells_part1.json','nb_cells_part2.json','nb_cells_part3.json',
             'nb_cells_part4.json','nb_cells_part5.json','nb_cells_part6.json']:
    with open(part, encoding='utf-8') as f:
        all_cells.extend(json.load(f))

print(f"Total cells assembled: {len(all_cells)}")
code_c = sum(1 for c in all_cells if c['cell_type']=='code')
md_c   = sum(1 for c in all_cells if c['cell_type']=='markdown')
print(f"Code cells: {code_c} | Markdown cells: {md_c}")

# Build notebook structure
nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name":"Python 3","language":"python","name":"python3"},
        "language_info": {"name":"python","version":"3.12.0"}
    },
    "cells": all_cells
}

out = 'research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)
print(f"Notebook saved: {out}")
print("Cell layout:")
for i, c in enumerate(all_cells):
    src = ''.join(c['source'])[:70].replace('\n',' ')
    print(f"  [{i:02d}] {c['cell_type'][:4]} | {src}")
