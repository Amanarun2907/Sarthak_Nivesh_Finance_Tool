# coding: utf-8
import json


nb = json.load(open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', encoding='utf-8'))
src = ''.join(nb['cells'][30]['source'])
lines = src.split('\n')
new_lines = []
for line in lines:
    # Fix: "ax2 = fig.add_subplot(...) agent_names = [..." -> split into two lines
    if 'fig.add_subplot' in line and 'agent_names' in line:
        idx = line.index('agent_names')
        new_lines.append(line[:idx].rstrip())
        new_lines.append(line[idx:])
    # Fix: "Benchmark']" orphan line -> merge with previous if it's a continuation
    elif line.strip() == "Benchmark']" and new_lines and 'agent_names' in new_lines[-1]:
        new_lines[-1] = new_lines[-1].rstrip() + ",'NIFTY 50 Benchmark']"
    else:
        new_lines.append(line)

src = '\n'.join(new_lines)
nb['cells'][30]['source'] = [src]
nb['cells'][30]['outputs'] = []
nb['cells'][30]['execution_count'] = None
with open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

# Verify
nb2 = json.load(open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', encoding='utf-8'))
src2 = ''.join(nb2['cells'][30]['source'])
lines2 = src2.split('\n')
for i, line in enumerate(lines2[29:36], 29):
    print(str(i) + ': ' + repr(line[:100]))
print('Fixed cell 30')
