"""
Execute only cell 13 (index 36) by running the full notebook
but only capturing output for the new cell.
We run the entire notebook so all variables are available.
"""
import subprocess, sys

result = subprocess.run(
    [sys.executable, '-m', 'jupyter', 'nbconvert',
     '--to', 'notebook',
     '--execute',
     '--inplace',
     '--ExecutePreprocessor.timeout=600',
     '--ExecutePreprocessor.kernel_name=python3',
     'research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb'],
    capture_output=True, text=True
)
print("STDOUT:", result.stdout[-2000:] if result.stdout else "(none)")
print("STDERR:", result.stderr[-3000:] if result.stderr else "(none)")
print("Return code:", result.returncode)
