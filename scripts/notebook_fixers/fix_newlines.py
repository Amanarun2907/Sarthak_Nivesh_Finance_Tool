# coding: utf-8
import json


nb = json.load(open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', encoding='utf-8'))

# Fix cell 30 (CELL 11) — replace literal backslash-n with actual newline in triple-quoted strings
src = ''.join(nb['cells'][30]['source'])

# These are inside Python string literals in the code — need to keep as \\n
# But the JSON had actual newlines which broke the Python syntax
# Replace actual newlines inside list literals with space
lines = src.split('\n')
fixed_lines = []
in_list = False
for line in lines:
    if 'agent_names = [' in line:
        in_list = True
    if in_list and ']' in line:
        in_list = False
    if in_list and line.strip() and not line.strip().startswith('#'):
        # This is inside the list — join with previous
        if fixed_lines:
            fixed_lines[-1] = fixed_lines[-1].rstrip() + ' ' + line.lstrip()
        else:
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

src = '\n'.join(fixed_lines)
nb['cells'][30]['source'] = [src]
nb['cells'][30]['outputs'] = []
nb['cells'][30]['execution_count'] = None

with open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)
print('Fixed cell 30 newline issues')
