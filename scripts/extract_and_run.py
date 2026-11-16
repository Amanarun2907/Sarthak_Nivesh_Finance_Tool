import json, os

nb = json.load(open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', encoding='utf-8'))
code_cells = [c for c in nb['cells'] if c['cell_type'] == 'code']

lines = ['import matplotlib\n', 'matplotlib.use("Agg")\n', 'import os\n', 'os.makedirs("research", exist_ok=True)\n\n']

for i, c in enumerate(code_cells):
    lines.append(f'\nprint("\\n" + "="*60)\n')
    lines.append(f'print("RUNNING CELL {i+1} of {len(code_cells)}")\n')
    lines.append(f'print("="*60)\n')
    src = ''.join(c['source'])
    # For the install cell: keep imports, skip subprocess/pip lines
    if 'subprocess' in src and 'pip' in src:
        filtered = []
        for line in src.split('\n'):
            if 'subprocess' in line or 'pip' in line or 'for p in' in line:
                continue
            filtered.append(line)
        src = '\n'.join(filtered)
    lines.append(src + '\n')

with open('research/run_all_cells.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print(f'Extracted {len(code_cells)} cells')
