"""
Execute the notebook from the project root.
This file is in the project root, so no chdir needed.
"""
import subprocess, sys, os

print("Working directory:", os.getcwd())

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
print("STDOUT:", result.stdout[-1500:] if result.stdout else "(none)")
if result.returncode != 0:
    print("STDERR (last 3000 chars):", result.stderr[-3000:] if result.stderr else "(none)")
else:
    print("SUCCESS! Notebook executed and saved with outputs.")
print("Return code:", result.returncode)
