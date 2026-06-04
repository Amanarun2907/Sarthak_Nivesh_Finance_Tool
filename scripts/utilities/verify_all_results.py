# coding: utf-8
"""Extract and print ALL outputs from the notebook for cross-verification"""
import json

nb = json.load(open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', encoding='utf-8'))

code_cells = [(i, c) for i, c in enumerate(nb['cells']) if c['cell_type'] == 'code']

print("=" * 70)
print("COMPLETE NOTEBOOK OUTPUT VERIFICATION")
print("=" * 70)

for cell_num, (idx, cell) in enumerate(code_cells, 1):
    outputs = cell.get('outputs', [])
    print(f"\n{'='*70}")
    print(f"CELL {cell_num} (notebook index {idx})")
    print(f"{'='*70}")
    
    # Print source preview
    src = ''.join(cell['source'])
    first_line = [l.strip() for l in src.split('\n') if l.strip() and not l.strip().startswith('#')]
    print(f"Code preview: {src.split(chr(10))[1].strip()[:80]}")
    
    # Print all text outputs
    for out in outputs:
        otype = out.get('output_type', '')
        if otype == 'stream':
            text = ''.join(out.get('text', []))
            print(f"\n[stdout]:\n{text[:3000]}")
        elif otype in ('execute_result', 'display_data'):
            if 'text/plain' in out.get('data', {}):
                txt = ''.join(out['data']['text/plain'])
                if len(txt) < 500:
                    print(f"\n[result]: {txt[:500]}")
            if 'image/png' in out.get('data', {}):
                print(f"[chart: embedded PNG, {len(out['data']['image/png'])} chars base64]")
        elif otype == 'error':
            print(f"\n[ERROR]: {out.get('ename')}: {out.get('evalue')}")
