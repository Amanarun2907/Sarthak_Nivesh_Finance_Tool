# coding: utf-8
import subprocess, sys, os
print('Working dir:', os.getcwd())

result = subprocess.run(
    [sys.executable, '-m', 'jupyter', 'nbconvert',
     '--to', 'notebook', '--execute', '--inplace',
     '--ExecutePreprocessor.timeout=600',
     '--ExecutePreprocessor.kernel_name=python3',
     'research/Dataset.ipynb'],
    capture_output=True, text=True
)
if result.returncode == 0:
    print('SUCCESS! Dataset.ipynb executed with all outputs.')
else:
    print('STDERR (last 2500):')
    print(result.stderr[-2500:])
print('Return code:', result.returncode)

