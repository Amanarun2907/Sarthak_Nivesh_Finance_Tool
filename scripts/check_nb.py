import json
nb = json.load(open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', encoding='utf-8'))
print('Total cells:', len(nb['cells']))
for i, c in enumerate(nb['cells']):
    src = c['source'][0][:55] if c['source'] else ''
    print(str(i+1) + '. [' + c['cell_type'] + '] ' + src)
