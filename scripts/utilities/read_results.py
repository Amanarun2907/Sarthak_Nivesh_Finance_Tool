# coding: utf-8
import json

nb = json.load(open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', encoding='utf-8'))

print("=" * 70)
print("NOTEBOOK EXECUTION RESULTS")
print("=" * 70)

code_cells = [(i, c) for i, c in enumerate(nb['cells']) if c['cell_type'] == 'code']
for i, (idx, cell) in enumerate(code_cells):
    outputs = cell.get('outputs', [])
    text_out = []
    has_img = False
    for o in outputs:
        if o.get('output_type') == 'stream':
            text_out.append(''.join(o.get('text', [])))
        elif o.get('output_type') in ['execute_result', 'display_data']:
            if 'image/png' in o.get('data', {}):
                has_img = True
            if 'text/plain' in o.get('data', {}):
                text_out.append(''.join(o['data']['text/plain']))
    
    src_preview = ''.join(cell['source'])[:60].replace('\n', ' ')
    print(f"\n--- Code Cell {i+1} (nb index {idx}) ---")
    print(f"Source: {src_preview}")
    print(f"Has image: {has_img} | Text outputs: {len(text_out)}")
    if text_out:
        combined = '\n'.join(text_out)
        # Print last 800 chars of text output
        print(combined[-800:] if len(combined) > 800 else combined)
