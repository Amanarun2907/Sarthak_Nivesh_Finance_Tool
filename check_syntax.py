# coding: utf-8
import json, ast

nb = json.load(open('research/Dataset.ipynb', encoding='utf-8'))
broken = []
for i, c in enumerate(nb['cells']):
    if c['cell_type'] == 'code':
        src = ''.join(c['source'])
        try:
            ast.parse(src)
        except SyntaxError as e:
            broken.append((i, e.lineno, str(e.msg)))

if broken:
    for i, ln, msg in broken:
        print('BROKEN cell ' + str(i) + ' line ' + str(ln) + ': ' + msg)
else:
    code_count = sum(1 for c in nb['cells'] if c['cell_type'] == 'code')
    print('ALL ' + str(code_count) + ' code cells syntax OK - ready to execute')
