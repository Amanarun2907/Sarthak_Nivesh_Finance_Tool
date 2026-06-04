import json, os
nb = json.load(open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', encoding='utf-8'))
c36 = nb['cells'][36]
print('Cell 36 (code cell 13) outputs:', len(c36.get('outputs', [])))
if c36.get('outputs'):
    for i, o in enumerate(c36['outputs'][:5]):
        otype = o.get('output_type')
        has_img = 'image/png' in str(o)
        has_text = 'text' in str(o)
        print(f'  Output {i}: type={otype}, has_image={has_img}, has_text={has_text}')
print('\nprediction_vs_actual.png exists:', os.path.exists('prediction_vs_actual.png'))
if os.path.exists('prediction_vs_actual.png'):
    print('  Size:', os.path.getsize('prediction_vs_actual.png'), 'bytes')
