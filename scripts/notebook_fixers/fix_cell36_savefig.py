import json
nb = json.load(open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', encoding='utf-8'))
src = ''.join(nb['cells'][36]['source'])
print("Before fix, savefig lines:")
for line in src.split('\n'):
    if 'savefig' in line:
        print("  ", line.strip())

# Remove the research/ prefixed line (keep only the plain filename one)
lines = src.split('\n')
new_lines = []
for line in lines:
    if 'plt.savefig("research/prediction_vs_actual.png"' in line:
        print("REMOVING:", line.strip())
        continue
    if "plt.savefig('research/prediction_vs_actual.png'" in line:
        print("REMOVING:", line.strip())
        continue
    new_lines.append(line)

src = '\n'.join(new_lines)
nb['cells'][36]['source'] = [src]

with open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("\nAfter fix, savefig lines:")
for line in src.split('\n'):
    if 'savefig' in line:
        print("  ", line.strip())
print("Done")
