# coding: utf-8
import json, ast


nb = json.load(open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', encoding='utf-8'))
src = ''.join(nb['cells'][36]['source'])
lines = src.split('\n')

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # Count single quotes (not escaped)
    sq = line.count("'") - line.count("\\'")
    dq = line.count('"') - line.count('\\"')
    # If odd single OR double quotes, merge with next line
    if (sq % 2 == 1 or dq % 2 == 1) and i+1 < len(lines):
        merged = line.rstrip() + lines[i+1].lstrip()
        new_lines.append(merged)
        i += 2
        continue
    new_lines.append(line)
    i += 1

src = '\n'.join(new_lines)
nb['cells'][36]['source'] = [src]
nb['cells'][36]['outputs'] = []
nb['cells'][36]['execution_count'] = None

# Check
try:
    ast.parse(src)
    print('Cell 36 syntax OK')
except SyntaxError as e:
    print(f'Cell 36 broken at line {e.lineno}: {e.msg}')
    lines2 = src.split('\n')
    for j in range(max(0,e.lineno-2), min(len(lines2), e.lineno+3)):
        print(f'  {j+1}: {repr(lines2[j][:100])}')

with open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)
print('Saved')
