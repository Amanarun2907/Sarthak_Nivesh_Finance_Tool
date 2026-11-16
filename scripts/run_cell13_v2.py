"""
Execute the notebook from the project root (not from research/ folder)
so all paths work correctly.
"""
import subprocess, sys, os

# Change to project root
os.chdir('..')
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
print("STDOUT:", result.stdout[-2000:] if result.stdout else "(none)")
if result.returncode != 0:
    print("STDERR:", result.stderr[-3000:] if result.stderr else "(none)")
print("Return code:", result.returncode)
