# coding: utf-8
import json, ast


def fix_broken_strings(src):
    """Fix lines where a string literal spans two lines due to embedded newlines."""
    lines = src.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Count unescaped single quotes - if odd, string is broken across lines
        # Simple heuristic: if line has odd number of single quotes and next line
        # doesn't start a new statement, merge them
        sq = line.count("'") - line.count("\\'")
        dq = line.count('"') - line.count('\\"')
        if (sq % 2 == 1 or dq % 2 == 1) and i + 1 < len(lines):
            # Merge with next line
            merged = line.rstrip() + lines[i+1].lstrip()
            new_lines.append(merged)
            i += 2
            continue
        new_lines.append(line)
        i += 1
    return '\n'.join(new_lines)

nb = json.load(open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', encoding='utf-8'))
fixed_count = 0

for idx, cell in enumerate(nb['cells']):
    if cell['cell_type'] != 'code':
        continue
    src = ''.join(cell['source'])
    # Check if it has syntax errors
    try:
        ast.parse(src)
        continue  # already fine
    except SyntaxError as e:
        pass

    # Apply fix iteratively
    for attempt in range(10):
        src = fix_broken_strings(src)
        try:
            ast.parse(src)
            nb['cells'][idx]['source'] = [src]
            nb['cells'][idx]['outputs'] = []
            nb['cells'][idx]['execution_count'] = None
            print(f'Fixed cell {idx} after {attempt+1} passes')
            fixed_count += 1
            break
        except SyntaxError as e:
            if attempt == 9:
                print(f'Cell {idx} still broken at line {e.lineno}: {e.msg}')
                lines = src.split('\n')
                for j in range(max(0,e.lineno-2), min(len(lines), e.lineno+2)):
                    print(f'  {j+1}: {repr(lines[j][:100])}')

with open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)
print(f'Done. Fixed {fixed_count} cells.')
