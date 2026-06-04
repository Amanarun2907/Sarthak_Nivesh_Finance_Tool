# coding: utf-8
import json


nb = json.load(open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', encoding='utf-8'))
src = ''.join(nb['cells'][30]['source'])

# Fix the broken agent_names line - find and replace the whole thing
lines = src.split('\n')
new_lines = []
skip_next = False
for i, line in enumerate(lines):
    if skip_next:
        skip_next = False
        continue
    # Fix the agent_names line that has duplicate NIFTY 50
    if 'agent_names' in line and 'NIFTY 50' in line:
        new_lines.append("agent_names = ['Agent 1 Stock Intel','Agent 2 Market','Agent 3 Smart Money','Agent 4 Sentiment','Combined Agentic AI','NIFTY 50 Benchmark']")
        # Skip the next line if it's a continuation of the broken list
        if i+1 < len(lines) and lines[i+1].strip().startswith("'NIFTY 50"):
            skip_next = True
    # Fix set_title lines with actual newlines inside strings
    elif "ax3.set_title('Agent Vote Distribution" in line and '(3+' not in line:
        new_lines.append("ax3.set_title('Agent Vote Distribution (3+ votes = BUY signal)')")
        skip_next = True  # skip the broken continuation
    elif "ax4.set_title('Drawdown Comparison" in line and 'How much' not in line:
        new_lines.append("ax4.set_title('Drawdown Comparison (How much did each strategy fall from peak?)')")
        skip_next = True
    else:
        new_lines.append(line)

src = '\n'.join(new_lines)
nb['cells'][30]['source'] = [src]
nb['cells'][30]['outputs'] = []
nb['cells'][30]['execution_count'] = None
with open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

# Quick syntax check
import ast
try:
    ast.parse(src)
    print('Syntax OK for cell 30')
except SyntaxError as e:
    print(f'Syntax error at line {e.lineno}: {e.msg}')
    lines2 = src.split('\n')
    for j in range(max(0,e.lineno-3), min(len(lines2), e.lineno+2)):
        print(f'  {j+1}: {repr(lines2[j][:100])}')
