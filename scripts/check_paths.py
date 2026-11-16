import json, re
nb = json.load(open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', encoding='utf-8'))
for i, c in enumerate(nb['cells']):
    if c['cell_type'] == 'code':
        src = ''.join(c['source'])
        if 'savefig' in src:
            paths = re.findall(r"savefig\(['\"]([^'\"]+)['\"]", src)
            print("Cell " + str(i) + ": " + str(paths))
