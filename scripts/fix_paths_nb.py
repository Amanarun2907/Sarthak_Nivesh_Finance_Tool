"""Fix savefig paths in notebook cells so they all use plain filenames
(notebook is executed from project root, so no research/ prefix needed inside nb)"""
import json

nb = json.load(open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', encoding='utf-8'))

def fix_src(src_list):
    src = ''.join(src_list)
    # Fix cell 12: research/agent2_backtest.png -> agent2_backtest.png
    src = src.replace("plt.savefig('research/agent2_backtest.png'", "plt.savefig('agent2_backtest.png'")
    src = src.replace('plt.savefig("research/agent2_backtest.png"', 'plt.savefig("agent2_backtest.png"')
    # Fix cell 36: keep only one savefig, remove the research/ prefixed one
    src = src.replace(
        'plt.savefig("research/prediction_vs_actual.png", dpi=150, bbox_inches="tight")\n    plt.savefig("prediction_vs_actual.png", dpi=150, bbox_inches="tight")',
        'plt.savefig("prediction_vs_actual.png", dpi=150, bbox_inches="tight")'
    )
    # Also handle single-quote version
    src = src.replace(
        "plt.savefig('research/prediction_vs_actual.png', dpi=150, bbox_inches='tight')\nplt.savefig('prediction_vs_actual.png', dpi=150, bbox_inches='tight')",
        "plt.savefig('prediction_vs_actual.png', dpi=150, bbox_inches='tight')"
    )
    return [src]

for i, c in enumerate(nb['cells']):
    if c['cell_type'] == 'code':
        src = ''.join(c['source'])
        if 'research/agent2_backtest.png' in src or 'research/prediction_vs_actual.png' in src:
            nb['cells'][i]['source'] = fix_src(c['source'])
            print("Fixed cell " + str(i))

with open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)
print("Done")
