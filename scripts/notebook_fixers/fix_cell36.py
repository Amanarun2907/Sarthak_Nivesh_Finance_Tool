# coding: utf-8
import json, ast


nb = json.load(open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', encoding='utf-8'))
src = ''.join(nb['cells'][36]['source'])
lines = src.split('\n')

# Find the agent_colors dict and verdicts dict - they have newlines in keys
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # Fix dict keys with embedded newlines - merge continuation lines
    sq = line.count("'") - line.count("\\'")
    dq = line.count('"') - line.count('\\"')
    # If odd quotes AND next line looks like a dict key continuation
    if (sq % 2 == 1) and i+1 < len(lines):
        next_line = lines[i+1]
        # Merge
        merged = line.rstrip() + next_line.lstrip()
        new_lines.append(merged)
        i += 2
        continue
    new_lines.append(line)
    i += 1

src = '\n'.join(new_lines)

# Now fix the agent_colors dict keys - replace newline-embedded keys with space
import re
# Replace "Agent 1\nStock Intel" style keys with "Agent 1 Stock Intel"
src = re.sub(r'"Agent (\d+)\n(\w[^"]*)"', r'"Agent \1 \2"', src)
src = re.sub(r'"Combined\nAgentic AI"', '"Combined Agentic AI"', src)

nb['cells'][36]['source'] = [src]
nb['cells'][36]['outputs'] = []
nb['cells'][36]['execution_count'] = None

try:
    ast.parse(src)
    print('Cell 36 syntax OK')
except SyntaxError as e:
    print(f'Cell 36 still broken at line {e.lineno}: {e.msg}')
    lines2 = src.split('\n')
    for j in range(max(0,e.lineno-3), min(len(lines2), e.lineno+3)):
        print(f'  {j+1}: {repr(lines2[j][:100])}')

with open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)
print('Saved')
