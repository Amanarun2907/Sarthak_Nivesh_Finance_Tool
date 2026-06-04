# coding: utf-8
import json

import ast

nb = json.load(open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', encoding='utf-8'))
src = ''.join(nb['cells'][30]['source'])
lines = src.split('\n')

# Find ALL broken set_title lines (where title string spans two lines)
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # Check if this line has an unclosed string in set_title
    if 'set_title(' in line and line.count("'") % 2 == 1 and i+1 < len(lines):
        # Merge with next line
        merged = line.rstrip() + lines[i+1].lstrip()
        new_lines.append(merged)
        i += 2
        continue
    new_lines.append(line)
    i += 1

src = '\n'.join(new_lines)
nb['cells'][30]['source'] = [src]
nb['cells'][30]['outputs'] = []
nb['cells'][30]['execution_count'] = None
with open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

try:
    ast.parse(src)
    print('Cell 30 syntax OK')
except SyntaxError as e:
    print(f'Still broken at line {e.lineno}: {e.msg}')
    lines2 = src.split('\n')
    for j in range(max(0,e.lineno-2), min(len(lines2), e.lineno+2)):
        print(f'  {j+1}: {repr(lines2[j][:100])}')
