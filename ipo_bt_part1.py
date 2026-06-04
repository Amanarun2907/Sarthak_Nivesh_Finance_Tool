
import sys, subprocess, os, warnings, json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats

for p in ['yfinance','pandas','numpy','matplotlib','seaborn',
          'requests','beautifulsoup4','vaderSentiment','textblob','scipy','nbformat']:
    subprocess.run([sys.executable,'-m','pip','install',p,'-q'],capture_output=True)

import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import seaborn as sns
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

warnings.filterwarnings("ignore")
VADER = SentimentIntensityAnalyzer()
OUT   = "research"
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "figure.facecolor":"white","axes.facecolor":"#F8F9FA",
    "axes.grid":True,"grid.alpha":0.3,"grid.color":"#CCCCCC",
    "font.family":"DejaVu Sans","font.size":11,
    "axes.titlesize":13,"axes.titleweight":"bold","axes.labelsize":11,
    "figure.dpi":130,"savefig.dpi":150,"savefig.bbox":"tight",
})
C = {"buy":"#00BFFF","strong_buy":"#00C853","hold":"#FF8F00",
     "sell":"#FF4757","strong_sell":"#B71C1C",
     "price":"#00BCD4","macro":"#4CAF50","sentiment":"#FFC107",
     "risk":"#9C27B0","ipo":"#FF5722","orch":"#FFC300",
     "win":"#43A047","loss":"#E53935"}

print("[1/9] Setup complete — all libraries loaded")
