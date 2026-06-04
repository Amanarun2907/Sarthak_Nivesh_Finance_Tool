import sys, subprocess, os, warnings, json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

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

warnings.filterwarnings("ignore")
VADER = SentimentIntensityAnalyzer()
OUT = "research"
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"figure.facecolor":"white","axes.facecolor":"#F8F9FA",
    "axes.grid":True,"grid.alpha":0.3,"font.family":"DejaVu Sans",
    "font.size":11,"axes.titlesize":13,"axes.titleweight":"bold",
    "savefig.dpi":150,"savefig.bbox":"tight"})
C={"buy":"#00BFFF","strong_buy":"#00C853","hold":"#FF8F00","sell":"#FF4757",
   "strong_sell":"#B71C1C","price":"#00BCD4","macro":"#4CAF50",
   "sentiment":"#FFC107","risk":"#9C27B0","ipo":"#FF5722","orch":"#FFC300",
   "win":"#43A047","loss":"#E53935"}
print("[1/9] Setup complete")

# ─── IPO DATASET ─────────────────────────────────────────────────────────────
RAW = [
    ('LIC',              'LICI.NS',       949,  872,   2.95,   2.83,  '2022-05-17'),
    ('Paytm',            'PAYTM.NS',      2150, 1955,  1.89,   2.79,  '2021-11-18'),
    ('Nykaa',            'NYKAA.NS',      1125, 2001,  82.0,   91.2,  '2021-11-10'),
    ('Zomato',           'ZOMATO.NS',     76,   116,   38.25,  51.8,  '2021-07-23'),
    ('Delhivery',        'DELHIVERY.NS',  487,  493,   1.63,   2.22,  '2022-05-24'),
    ('Adani Wilmar',     'AWL.NS',        230,  227,   17.5,   7.62,  '2022-02-08'),
    ('Devyani Intl',     'DEVYANI.NS',    90,   140,   116.7, 144.5,  '2021-08-16'),
    ('Policybazaar',     'POLICYBZR.NS',  980,  1150,  16.6,  22.5,   '2021-11-15'),
    ('Paradeep Phos',    'PARADEEP.NS',   42,   50,    107.1, 153.4,  '2022-05-12'),
    ('Rainbow Childrn',  'RAINBOW.NS',    542,  628,   43.0,   50.2,  '2022-05-10'),
    ('Campus Activwear', 'CAMPUS.NS',     292,  370,   51.75,  68.5,  '2022-04-28'),
    ('Vedant Fashions',  'MANYAVAR.NS',   866,  1008,  66.0,   98.2,  '2022-02-16'),
    ('Medplus Health',   'MEDPLUS.NS',    796,  1008,  52.6,   64.3,  '2021-12-23'),
    ('Go Fashion',       'GOCOLORS.NS',   690,  1035,  135.5, 176.3,  '2021-11-30'),
    ('Latent View',      'LATENTVIEW.NS', 197,  512,   326.5, 409.1,  '2021-11-23'),
    ('Fino Payments',    'FINOPB.NS',     577,  544,   2.6,   3.4,    '2021-11-12'),
    ('Ethos Ltd',        'ETHOS.NS',      878,  1200,  9.4,   13.5,   '2022-05-30'),
    ('Hyundai India',    'HYUNDAI.NS',    1960, 1934,  17.4,  36.5,   '2024-10-22'),
    ('Bajaj Hsg Fin',    'BAJAJHFL.NS',   70,   150,   67.4,  208.0,  '2024-09-16'),
    ('Swiggy',           'SWIGGY.NS',     390,  420,   3.6,   6.0,    '2024-11-13'),
    ('Ola Electric',     'OLAELEC.NS',    76,   76,    4.27,  5.5,    '2024-08-09'),
    ('Firstcry',         'BRAINBEES.NS',  465,  596,   12.2,  18.7,   '2024-08-13'),
    ('Premier Energies', 'PREMIERENE.NS', 450,  910,   74.1,  120.5,  '2024-09-03'),
    ('Waaree Energies',  'WAAREEENER.NS', 1503, 2550,  69.5,  199.2,  '2024-10-28'),
    ('NTPC Green',       'NTPCGREEN.NS',  108,  111,   2.55,  3.3,    '2024-11-27'),
]
COLS = ['name','symbol','issue','listing','sub','qib','date']
df0 = pd.DataFrame(RAW, columns=COLS)
df0['ret_list']    = (df0['listing'] - df0['issue']) / df0['issue'] * 100
df0['listing_date']= pd.to_datetime(df0['date'])
print(f"[2/9] Dataset: {len(df0)} IPOs | Avg listing gain: {df0.ret_list.mean():.1f}%")
