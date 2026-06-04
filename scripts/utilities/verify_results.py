import json
nb = json.load(open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', encoding='utf-8'))

print("=" * 65)
print("NOTEBOOK VERIFICATION — Enhanced Results")
print("=" * 65)

code_cells = [(i, c) for i, c in enumerate(nb['cells']) if c['cell_type'] == 'code']
print(f"Total cells: {len(nb['cells'])} | Code: {len(code_cells)}")
print()

for i, c in code_cells:
    outputs = c.get('outputs', [])
    has_img = any('image/png' in str(o) for o in outputs)
    # Extract text output
    text_out = ""
    for o in outputs:
        if o.get('output_type') == 'stream':
            text_out += ''.join(o.get('text', []))
        elif o.get('output_type') == 'execute_result':
            text_out += str(o.get('data', {}).get('text/plain', ''))
    # Show key lines
    key_lines = [l.strip() for l in text_out.split('\n')
                 if any(k in l for k in ['Return', 'Sharpe', 'Drawdown', 'ACCURACY',
                                          'Agent', 'Combined', 'p-value', 'significant',
                                          'accuracy', 'Outperform', 'saved'])]
    src_preview = ''.join(c['source'])[:50].replace('\n', ' ')
    print(f"Cell {i:2d} | img={has_img} | {src_preview}")
    for l in key_lines[:8]:
        print(f"         {l}")
    print()
