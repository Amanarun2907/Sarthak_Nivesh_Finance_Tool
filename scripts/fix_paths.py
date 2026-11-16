content = open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', encoding='utf-8').read()
for agent in ['agent1','agent2','agent3','agent4','agent5','agent6','combined_agentic_ai']:
    old = f"research/{agent}_backtest.png"
    new = f"{agent}_backtest.png"
    content = content.replace(old, new)
open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', 'w', encoding='utf-8').write(content)
print('Fixed all savefig paths')
