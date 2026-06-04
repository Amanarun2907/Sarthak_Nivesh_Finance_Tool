# coding: utf-8
import json, ast

nb = json.load(open('research/Dataset.ipynb', encoding='utf-8'))

# ── Fix cell 37: architecture diagram arrow_map list ─────────────────────────
src37 = ''.join(nb['cells'][37]['source'])
lines37 = src37.split('\n')
new37 = []
i = 0
while i < len(lines37):
    line = lines37[i]
    if 'arrow_map = [' in line:
        # Collect until the closing ]
        combined = line
        i += 1
        while i < len(lines37):
            combined += '\n' + lines37[i]
            if lines37[i].strip() == ']':
                i += 1
                break
            i += 1
        new37.append(combined)
        continue
    new37.append(line)
    i += 1
src37 = '\n'.join(new37)
try:
    ast.parse(src37)
    print('Cell 37 syntax OK')
except SyntaxError as e:
    print('Cell 37 broken at line ' + str(e.lineno) + ': ' + str(e.msg))
    ls = src37.split('\n')
    for j in range(max(0,e.lineno-2), min(len(ls), e.lineno+3)):
        print('  ' + str(j+1) + ': ' + repr(ls[j][:90]))
nb['cells'][37]['source'] = [src37]
nb['cells'][37]['outputs'] = []
nb['cells'][37]['execution_count'] = None

# ── Fix cell 43: VADER labels list ───────────────────────────────────────────
src43 = ''.join(nb['cells'][43]['source'])
lines43 = src43.split('\n')
new43 = []
i = 0
while i < len(lines43):
    line = lines43[i]
    # Detect broken labels = [...] spanning multiple lines
    if '    labels = [' in line and i+1 < len(lines43):
        sq = line.count("'") - line.count("\\'")
        if sq % 2 == 1:
            # Merge until balanced
            combined = line
            i += 1
            while i < len(lines43):
                combined += lines43[i]
                sq2 = combined.count("'") - combined.count("\\'")
                if sq2 % 2 == 0 and ']' in combined:
                    i += 1
                    break
                i += 1
            # Replace with clean version
            new43.append("    labels = ['Positive (score>+0.05)', 'Negative (score<-0.05)', 'Neutral (-0.05 to +0.05)']")
            continue
    new43.append(line)
    i += 1
src43 = '\n'.join(new43)
try:
    ast.parse(src43)
    print('Cell 43 syntax OK')
except SyntaxError as e:
    print('Cell 43 broken at line ' + str(e.lineno) + ': ' + str(e.msg))
    ls = src43.split('\n')
    for j in range(max(0,e.lineno-2), min(len(ls), e.lineno+3)):
        print('  ' + str(j+1) + ': ' + repr(ls[j][:90]))
nb['cells'][43]['source'] = [src43]
nb['cells'][43]['outputs'] = []
nb['cells'][43]['execution_count'] = None

with open('research/Dataset.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)
print('Saved')
