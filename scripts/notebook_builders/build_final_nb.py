# coding: utf-8
"""
Build the FINAL definitive backtesting notebook.
Matches EXACTLY the web interface implementation (agentic.py, stocks.py, smart_money.py, analytics.py).
"""
import json

# ─────────────────────────────────────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────────────────────────────────────
def code_cell(src, cid):
    return {"cell_type":"code","execution_count":None,"id":cid,
            "metadata":{},"outputs":[],"source":[src]}

def md_cell(src, cid):
    return {"cell_type":"markdown","id":cid,"metadata":{},"source":[src]}

cells = []

