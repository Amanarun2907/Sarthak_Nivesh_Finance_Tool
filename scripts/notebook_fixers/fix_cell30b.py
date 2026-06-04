# coding: utf-8
import json


nb = json.load(open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', encoding='utf-8'))
src = ''.join(nb['cells'][30]['source'])
lines = src.split('\n')

# Find and fix the broken table_data header (lines 71-79)
# Join lines 72-79 into one proper line
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # Detect start of broken table header
    if line.strip() == "['Metric','Agent 1" or (i > 0 and lines[i-1].strip() == 'table_data = [' and line.strip().startswith("['Metric")):
        # Collect until we find the closing '],'
        combined = line
        i += 1
        while i < len(lines) and not lines[i].strip().endswith('],'):
            combined = combined.rstrip() + lines[i].strip()
            i += 1
        if i < len(lines):
            combined = combined.rstrip() + lines[i].strip()
        # Replace with clean version
        new_lines.append("    ['Metric','Agent 1 Stock Intel','Agent 2 Market','Agent 3 Smart Money','Agent 4 Sentiment','Combined Agentic AI','NIFTY 50 Benchmark'],")
        i += 1
        continue
    new_lines.append(line)
    i += 1

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
for i2, line2 in enumerate(lines2[70:82], 70):
    print(str(i2) + ': ' + repr(line2[:100]))
print('Fixed table_data in cell 30')
