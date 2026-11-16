# Smart Money Tracker - Real-time FII/DII from NSE
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import yfinance as yf
import re
import plotly.graph_objects as go

INDIAN_STOCKS = {
    "RELIANCE.NS": "Reliance", "TCS.NS": "TCS", "HDFCBANK.NS": "HDFC Bank",
    "INFY.NS": "Infosys", "ICICIBANK.NS": "ICICI Bank",
    "HINDUNILVR.NS": "Hindustan Unilever", "ITC.NS": "ITC", "SBIN.NS": "SBI",
    "BHARTIARTL.NS": "Bharti Airtel", "KOTAKBANK.NS": "Kotak Bank",
    "LT.NS": "L&T", "AXISBANK.NS": "Axis Bank", "ASIANPAINT.NS": "Asian Paints",
    "MARUTI.NS": "Maruti", "TITAN.NS": "Titan", "BAJFINANCE.NS": "Bajaj Finance",
    "WIPRO.NS": "Wipro", "ULTRACEMCO.NS": "UltraTech",
    "NESTLEIND.NS": "Nestle", "HCLTECH.NS": "HCL Tech",
}

_HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}


def _n(v):
    try:
        v = str(v).replace(",", "").replace("(", "-").replace(")", "").strip()
        m = re.findall(r"-?\d+\.?\d*", v)
        return float(m[0]) if m else 0.0
    except Exception:
        return 0.0


class LiveSmartMoneyTracker:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(_HDR)

    def _parse_nse(self, data):
        """
        NSE real API format (verified working):
        [{"category":"DII","date":"08-Apr-2026","buyValue":"29003.39",
          "sellValue":"24835.22","netValue":"4168.17"},
         {"category":"FII/FPI","date":"08-Apr-2026","buyValue":"19092.05",
          "sellValue":"21904.02","netValue":"-2811.97"}]
        """
        fii = next((x for x in data if "FII" in x.get("category", "").upper()), None)
        dii = next((x for x in data if "DII" in x.get("category", "").upper()), None)
        if not fii and not dii:
            return None
        date     = (fii or dii).get("date", datetime.now().strftime("%d-%b-%Y"))
        fii_buy  = _n((fii or {}).get("buyValue",  0))
        fii_sell = _n((fii or {}).get("sellValue", 0))
        fii_net  = _n((fii or {}).get("netValue",  0))
        dii_buy  = _n((dii or {}).get("buyValue",  0))
        dii_sell = _n((dii or {}).get("sellValue", 0))
        dii_net  = _n((dii or {}).get("netValue",  0))
        if fii_net == 0 and (fii_buy or fii_sell):
            fii_net = fii_buy - fii_sell
        if dii_net == 0 and (dii_buy or dii_sell):
            dii_net = dii_buy - dii_sell
        if all(v == 0 for v in [fii_buy, fii_sell, fii_net, dii_buy, dii_sell, dii_net]):
            return None
        return {
            "date": date,
            "fii_buy": fii_buy, "fii_sell": fii_sell, "fii_net": fii_net,
            "dii_buy": dii_buy, "dii_sell": dii_sell, "dii_net": dii_net,
            "source": "NSE (Live)",
        }

    def _today_from_nse(self):
        try:
            r = self.session.get(
                "https://www.nseindia.com/api/fiidiiTradeReact", timeout=15
            )
            if r.status_code == 200:
                data = r.json()
                if data:
                    return self._parse_nse(data)
        except Exception as e:
            print("NSE error:", e)
        return None

    def _today_from_samco(self):
        try:
            hdrs = dict(_HDR)
            hdrs["Referer"] = "https://www.google.com/"
            r = requests.get(
                "https://www.samco.in/knowledge-center/articles/fii-dii-data/",
                headers=hdrs, timeout=12
            )
            if r.status_code != 200:
                return None
            soup = BeautifulSoup(r.text, "html.parser")
            fii_net = dii_net = None
            for table in soup.find_all("table"):
                for row in table.find_all("tr"):
                    cols = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
                    if len(cols) >= 2:
                        lbl = cols[0].upper()
                        val = _n(cols[1])
                        if "FII" in lbl:
                            fii_net = val
                        elif "DII" in lbl:
                            dii_net = val
            if fii_net is not None and dii_net is not None:
                return {
                    "date": datetime.now().strftime("%d-%b-%Y"),
                    "fii_buy": 0, "fii_sell": 0, "fii_net": fii_net,
                    "dii_buy": 0, "dii_sell": 0, "dii_net": dii_net,
                    "source": "Samco",
                }
        except Exception as e:
            print("Samco error:", e)
        return None

    def _nifty_history(self, today_row, days=19):
        """
        Build estimated historical FII/DII using Nifty 50 daily returns.
        Anchored to today's real values. Clearly labelled 'Estimated'.
        """
        try:
            hist = yf.Ticker("^NSEI").history(period="1mo")
            if hist.empty or len(hist) < 3:
                return []
            chg_today = float(hist["Close"].iloc[-1] - hist["Close"].iloc[-2])
            fii_scale = (today_row["fii_net"] / chg_today) if chg_today != 0 else 500
            dii_scale = (today_row["dii_net"] / chg_today) if chg_today != 0 else -300
            rows = []
            for i in range(1, min(len(hist) - 1, days + 1)):
                idx = -(i + 1)
                chg = float(hist["Close"].iloc[idx] - hist["Close"].iloc[idx - 1])
                rows.append({
                    "date":     hist.index[idx].strftime("%d-%b-%Y"),
                    "fii_buy":  0, "fii_sell": 0,
                    "fii_net":  round(chg * fii_scale, 2),
                    "dii_buy":  0, "dii_sell": 0,
                    "dii_net":  round(chg * dii_scale, 2),
                    "source":   "Estimated",
                })
            return rows
        except Exception as e:
            print("Nifty proxy error:", e)
            return []

    def fetch_live_fii_dii_data(self):
        today = self._today_from_nse()
        if not today:
            print("NSE failed, trying Samco...")
            today = self._today_from_samco()
        if not today:
            return pd.DataFrame()
        history = self._nifty_history(today, days=19)
        return pd.DataFrame([today] + history)

    def fetch_live_bulk_deals(self):
        try:
            r = self.session.get(
                "https://www.nseindia.com/api/snapshot-capital-market-largedeal",
                timeout=15
            )
            if r.status_code == 200:
                deals = r.json().get("BULK_DEAL_DATA", [])
                if deals:
                    recs = []
                    for d in deals:
                        try:
                            recs.append({
                                "symbol": d.get("symbol", ""),
                                "company": d.get("companyName", ""),
                                "client_name": d.get("clientName", ""),
                                "deal_type": d.get("dealType", ""),
                                "quantity": float(d.get("quantity", 0) or 0),
                                "price": float(d.get("tradePrice", 0) or 0),
                                "date": d.get("dealDate", ""),
                            })
                        except Exception:
                            continue
                    if recs:
                        return pd.DataFrame(recs)
        except Exception as e:
            print("Bulk deals error:", e)
        return pd.DataFrame()

    def fetch_live_block_deals(self):
        try:
            r = self.session.get(
                "https://www.nseindia.com/api/snapshot-capital-market-largedeal",
                timeout=15
            )
            if r.status_code == 200:
                deals = r.json().get("BLOCK_DEAL_DATA", [])
                if deals:
                    recs = []
                    for d in deals:
                        try:
                            recs.append({
                                "symbol": d.get("symbol", ""),
                                "company": d.get("companyName", ""),
                                "client_name": d.get("clientName", ""),
                                "quantity": float(d.get("quantity", 0) or 0),
                                "price": float(d.get("tradePrice", 0) or 0),
                                "date": d.get("dealDate", ""),
                            })
                        except Exception:
                            continue
                    if recs:
                        return pd.DataFrame(recs)
        except Exception as e:
            print("Block deals error:", e)
        return pd.DataFrame()

    def get_stock_volume_analysis(self, symbol):
        try:
            hist = yf.Ticker(symbol).history(period="30d")
            if not hist.empty and len(hist) > 5:
                cv = float(hist["Volume"].iloc[-1])
                av = float(hist["Volume"].mean())
                cp = float(hist["Close"].iloc[-1])
                pc = ((cp - float(hist["Close"].iloc[0])) / float(hist["Close"].iloc[0])) * 100
                vr = cv / av if av > 0 else 1
                return {
                    "symbol": symbol, "company": INDIAN_STOCKS.get(symbol, symbol),
                    "current_price": cp, "volume_ratio": vr, "price_change_30d": pc,
                    "avg_volume": av, "current_volume": cv,
                    "signal": "High Activity" if vr > 1.5 else "Normal",
                }
        except Exception:
            pass
        return None

    def detect_unusual_activity(self):
        results = [
            a for sym in list(INDIAN_STOCKS.keys())[:15]
            for a in [self.get_stock_volume_analysis(sym)]
            if a and a["volume_ratio"] > 1.5
        ]
        return pd.DataFrame(results) if results else pd.DataFrame()

    def get_sector_flow_analysis(self):
        sectors = {
            "Banking": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
            "IT": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS"],
            "Auto": ["MARUTI.NS"],
            "FMCG": ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS"],
            "Finance": ["BAJFINANCE.NS"],
        }
        rows = []
        for sector, stocks in sectors.items():
            vols, pxs, cnt = [], [], 0
            for sym in stocks:
                a = self.get_stock_volume_analysis(sym)
                if a:
                    vols.append(a["volume_ratio"])
                    pxs.append(a["price_change_30d"])
                    cnt += 1
            if cnt:
                av, ap = sum(vols) / cnt, sum(pxs) / cnt
                if av > 1.3 and ap > 2:
                    sig, col = "Strong Buy", "#00ff88"
                elif av > 1.1 and ap > 0:
                    sig, col = "Buy", "#17a2b8"
                elif ap < -2:
                    sig, col = "Sell", "#ff5252"
                else:
                    sig, col = "Hold", "#ffc107"
                rows.append({
                    "sector": sector, "avg_volume_ratio": av,
                    "avg_price_change": ap, "signal": sig,
                    "color": col, "stocks_analyzed": cnt,
                })
        return pd.DataFrame(rows) if rows else pd.DataFrame()

    def generate_smart_money_signals(self, fii_dii_df, bulk_df, block_df):
        signals = []
        if not fii_dii_df.empty:
            fn = fii_dii_df.iloc[0]["fii_net"]
            dn = fii_dii_df.iloc[0]["dii_net"]
            if fn > 1000 and dn > 1000:
                signals.append({"signal": "STRONG BUY", "reason": "Both FII & DII buying heavily", "confidence": 90, "color": "#00ff88"})
            elif fn > 0 and dn > 0:
                signals.append({"signal": "BUY", "reason": "Both FII & DII net buyers", "confidence": 78, "color": "#17a2b8"})
            elif fn < -2000 and dn < 0:
                signals.append({"signal": "SELL", "reason": "Both FII & DII selling", "confidence": 85, "color": "#ff5252"})
            else:
                signals.append({"signal": "HOLD", "reason": "Mixed institutional signals", "confidence": 60, "color": "#ffc107"})
        return signals or [{"signal": "HOLD", "reason": "Insufficient data", "confidence": 50, "color": "#ffc107"}]


# ── UI ────────────────────────────────────────────────────────────────────────

def show_live_smart_money_tracker():
    st.header("💰 Smart Money Tracker — Live Institutional Flow")

    st.markdown("""
    <div style='background:linear-gradient(135deg,#667eea,#764ba2);
                padding:1.5rem;border-radius:15px;margin-bottom:1.5rem;'>
        <h2 style='color:#fff;margin:0;text-align:center;'>
            FOLLOW THE SMART MONEY — LIVE DATA
        </h2>
        <p style='color:#e0e0e0;margin:0.4rem 0 0 0;text-align:center;'>
            NSE API (real-time) | Bulk & Block Deals | Volume Intelligence | Sector Flow
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_btn, col_ts = st.columns([4, 1])
    with col_btn:
        if st.button("🔄 Refresh Live Data", type="primary", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with col_ts:
        st.caption("🕐 " + datetime.now().strftime("%d %b %Y  %H:%M:%S"))

    tracker = LiveSmartMoneyTracker()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 FII / DII Flow",
        "💼 Bulk Deals",
        "🔒 Block Deals",
        "📈 Volume Analysis",
        "🏭 Sector Flow",
    ])

    # ── TAB 1 ─────────────────────────────────────────────────────────────────
    with tab1:
        st.subheader("📊 Foreign & Domestic Institutional Investor Flow")

        with st.spinner("Fetching live FII/DII data from NSE..."):
            df = tracker.fetch_live_fii_dii_data()

        if df.empty:
            st.error(
                "Could not fetch FII/DII data from any source right now.\n\n"
                "This usually happens when:\n"
                "- Market is closed (weekend / holiday)\n"
                "- NSE/BSE servers are under maintenance\n"
                "- Network is blocking scraping\n\n"
                "Please try refreshing after a few minutes."
            )
        else:
            today = df.iloc[0]
            source = today.get("source", "NSE")
            fn = today["fii_net"]
            dn = today["dii_net"]
            total = fn + dn

            # Signal
            if fn > 1000 and dn > 1000:
                signal, sig_col = "STRONG BUY", "#00ff88"
            elif fn > 0 and dn > 0:
                signal, sig_col = "BUY", "#17a2b8"
            elif fn < -1000 and dn < -1000:
                signal, sig_col = "STRONG SELL", "#ff5252"
            elif fn < 0 and dn < 0:
                signal, sig_col = "SELL", "#ff9800"
            else:
                signal, sig_col = "MIXED", "#ffc107"

            st.success(
                "✅ Live FII/DII data — Source: **" + source + "** — "
                "Date: **" + str(today["date"]) + "**"
            )
            st.info(
                "ℹ️ **Data transparency:** Row 1 shows today's real NSE data. "
                "The remaining rows are **Nifty-proxy estimates** (calculated from Nifty 50 daily returns) "
                "because NSE only publishes the current day's FII/DII figures via their public API. "
                "These estimates are clearly labelled 'Estimated' in the table and shown as faded bars in the chart."
            )

            # KPI cards
            c1, c2, c3, c4 = st.columns(4)
            for col, label, net, buy, sell, color in [
                (c1, "FII Net",   fn,    today["fii_buy"], today["fii_sell"], "#00ff88" if fn >= 0 else "#ff5252"),
                (c2, "DII Net",   dn,    today["dii_buy"], today["dii_sell"], "#00ff88" if dn >= 0 else "#ff5252"),
                (c3, "Total Net", total, today["fii_buy"] + today["dii_buy"],
                                         today["fii_sell"] + today["dii_sell"],
                                         "#00ff88" if total >= 0 else "#ff5252"),
            ]:
                buy_str  = ("₹{:,.0f} Cr".format(buy))  if buy  else "N/A"
                sell_str = ("₹{:,.0f} Cr".format(sell)) if sell else "N/A"
                col.markdown(
                    "<div style='background:rgba(0,212,255,0.08);padding:1.2rem;"
                    "border-radius:12px;border-left:5px solid " + color + ";'>"
                    "<h4 style='color:#00d4ff;margin:0;'>" + label + "</h4>"
                    "<h2 style='color:" + color + ";margin:0.4rem 0;'>₹{:,.0f} Cr</h2>".format(net) +
                    "<p style='color:#ccc;margin:0;font-size:0.82rem;'>"
                    "Buy: " + buy_str + " | Sell: " + sell_str + "</p></div>",
                    unsafe_allow_html=True
                )

            c4.markdown(
                "<div style='background:rgba(0,212,255,0.08);padding:1.2rem;"
                "border-radius:12px;border-left:5px solid " + sig_col + ";'>"
                "<h4 style='color:#00d4ff;margin:0;'>Market Signal</h4>"
                "<h2 style='color:" + sig_col + ";margin:0.4rem 0;'>" + signal + "</h2>"
                "<p style='color:#ccc;margin:0;font-size:0.82rem;'>Based on institutional flow</p></div>",
                unsafe_allow_html=True
            )

            # Bar chart — today real + history estimated
            real_rows = df[df["source"] != "Estimated"]
            est_rows  = df[df["source"] == "Estimated"]

            fig = go.Figure()
            # Real data bars (solid)
            if not real_rows.empty:
                fig.add_trace(go.Bar(
                    x=real_rows["date"], y=real_rows["fii_net"],
                    name="FII Net (Real)",
                    marker_color=["#00ff88" if v >= 0 else "#ff5252" for v in real_rows["fii_net"]],
                    text=["₹{:,.0f}".format(v) for v in real_rows["fii_net"]],
                    textposition="outside"
                ))
                fig.add_trace(go.Bar(
                    x=real_rows["date"], y=real_rows["dii_net"],
                    name="DII Net (Real)",
                    marker_color=["#00d4ff" if v >= 0 else "#ff9800" for v in real_rows["dii_net"]],
                    text=["₹{:,.0f}".format(v) for v in real_rows["dii_net"]],
                    textposition="outside"
                ))
            # Estimated bars (semi-transparent)
            if not est_rows.empty:
                fig.add_trace(go.Bar(
                    x=est_rows["date"], y=est_rows["fii_net"],
                    name="FII Net (Est.)",
                    marker_color="rgba(0,255,136,0.35)",
                    opacity=0.6
                ))
                fig.add_trace(go.Bar(
                    x=est_rows["date"], y=est_rows["dii_net"],
                    name="DII Net (Est.)",
                    marker_color="rgba(0,212,255,0.35)",
                    opacity=0.6
                ))

            fig.update_layout(
                title="FII & DII Net Flow — ₹ Crores (Solid = Real NSE | Faded = Nifty-based estimate)",
                barmode="group", template="plotly_dark", height=420,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                yaxis_title="₹ Crores", xaxis_tickangle=-35
            )
            fig.add_hline(y=0, line_dash="dash", line_color="#555")
            st.plotly_chart(fig, use_container_width=True)

            # Cumulative line chart
            df2 = df.copy()
            df2["fii_cum"] = df2["fii_net"].cumsum()
            df2["dii_cum"] = df2["dii_net"].cumsum()
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=df2["date"], y=df2["fii_cum"], name="FII Cumulative",
                line=dict(color="#00d4ff", width=2),
                fill="tozeroy", fillcolor="rgba(0,212,255,0.08)"
            ))
            fig2.add_trace(go.Scatter(
                x=df2["date"], y=df2["dii_cum"], name="DII Cumulative",
                line=dict(color="#00ff88", width=2),
                fill="tozeroy", fillcolor="rgba(0,255,136,0.08)"
            ))
            fig2.update_layout(
                title="Cumulative FII & DII Flow (₹ Crores)",
                template="plotly_dark", height=350,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig2, use_container_width=True)

            # Full table
            st.markdown("### 📋 FII/DII Data Table")
            disp = df[["date", "fii_buy", "fii_sell", "fii_net",
                        "dii_buy", "dii_sell", "dii_net", "source"]].rename(columns={
                "date": "Date", "fii_buy": "FII Buy (Cr)", "fii_sell": "FII Sell (Cr)",
                "fii_net": "FII Net (Cr)", "dii_buy": "DII Buy (Cr)",
                "dii_sell": "DII Sell (Cr)", "dii_net": "DII Net (Cr)", "source": "Source"
            })
            st.dataframe(disp, use_container_width=True)
            st.caption(
                "Row 1 = Real-time NSE data | Remaining rows = Nifty-proxy estimates | "
                "Updated: " + datetime.now().strftime("%H:%M:%S")
            )

    # ── TAB 2 ─────────────────────────────────────────────────────────────────
    with tab2:
        st.subheader("💼 Bulk Deals — Large Institutional Trades")
        with st.spinner("Fetching live bulk deals from NSE..."):
            bulk_df = tracker.fetch_live_bulk_deals()
        if not bulk_df.empty:
            st.success("✅ " + str(len(bulk_df)) + " bulk deals found")
            for _, d in bulk_df.iterrows():
                color = "#00ff88" if "BUY" in str(d.get("deal_type", "")).upper() else "#ff5252"
                st.markdown(
                    "<div style='background:rgba(0,212,255,0.08);padding:1rem;"
                    "border-radius:10px;border-left:5px solid " + color + ";margin:0.5rem 0;'>"
                    "<b style='color:#00d4ff;'>" + str(d.get("company","")) + " (" + str(d.get("symbol","")) + ")</b><br>"
                    "Client: " + str(d.get("client_name","N/A")) + " | "
                    "Type: <b style='color:" + color + ";'>" + str(d.get("deal_type","N/A")) + "</b> | "
                    "Qty: {:,.0f}".format(d.get("quantity", 0)) + " | "
                    "Price: ₹{:.2f}".format(d.get("price", 0)) + " | "
                    "Date: " + str(d.get("date","")) + "</div>",
                    unsafe_allow_html=True
                )
        else:
            st.info("No bulk deals today or NSE data not yet available.")

    # ── TAB 3 ─────────────────────────────────────────────────────────────────
    with tab3:
        st.subheader("🔒 Block Deals — Off-Market Institutional Trades")
        with st.spinner("Fetching live block deals from NSE..."):
            block_df = tracker.fetch_live_block_deals()
        if not block_df.empty:
            st.success("✅ " + str(len(block_df)) + " block deals found")
            for _, d in block_df.iterrows():
                st.markdown(
                    "<div style='background:rgba(0,212,255,0.08);padding:1rem;"
                    "border-radius:10px;border-left:5px solid #764ba2;margin:0.5rem 0;'>"
                    "<b style='color:#00d4ff;'>" + str(d.get("company","")) + " (" + str(d.get("symbol","")) + ")</b><br>"
                    "Client: " + str(d.get("client_name","N/A")) + " | "
                    "Qty: {:,.0f}".format(d.get("quantity", 0)) + " | "
                    "Price: ₹{:.2f}".format(d.get("price", 0)) + " | "
                    "Date: " + str(d.get("date","")) + "</div>",
                    unsafe_allow_html=True
                )
        else:
            st.info("No block deals today or NSE data not yet available.")

    # ── TAB 4 ─────────────────────────────────────────────────────────────────
    with tab4:
        st.subheader("📈 Unusual Volume Activity")
        with st.spinner("Analysing volume across top 15 stocks..."):
            unusual_df = tracker.detect_unusual_activity()
        if not unusual_df.empty:
            st.success("✅ " + str(len(unusual_df)) + " stocks with unusual volume")
            for _, s in unusual_df.iterrows():
                vc = "#00ff88" if s["volume_ratio"] > 2 else "#17a2b8"
                pc = "#00ff88" if s["price_change_30d"] > 0 else "#ff5252"
                st.markdown(
                    "<div style='background:rgba(0,212,255,0.08);padding:1rem;"
                    "border-radius:10px;border-left:5px solid " + vc + ";margin:0.5rem 0;'>"
                    "<b style='color:#00d4ff;'>" + str(s["company"]) + " (" + str(s["symbol"]).replace(".NS","") + ")</b>"
                    " ₹{:.2f}".format(s["current_price"]) + " | "
                    "Volume: <b style='color:" + vc + ";'>{:.2f}x normal</b>".format(s["volume_ratio"]) + " | "
                    "30d: <b style='color:" + pc + ";'>{:+.2f}%</b>".format(s["price_change_30d"]) + " | "
                    + str(s["signal"]) + "</div>",
                    unsafe_allow_html=True
                )
        else:
            st.info("No unusual volume activity detected right now.")

    # ── TAB 5 ─────────────────────────────────────────────────────────────────
    with tab5:
        st.subheader("🏭 Sector-wise Money Flow Analysis")
        with st.spinner("Analysing sector flows..."):
            sector_df = tracker.get_sector_flow_analysis()
        if not sector_df.empty:
            st.success("✅ " + str(len(sector_df)) + " sectors analysed")
            for _, s in sector_df.iterrows():
                st.markdown(
                    "<div style='background:rgba(0,212,255,0.08);padding:1.2rem;"
                    "border-radius:12px;border-left:5px solid " + s["color"] + ";margin:0.8rem 0;'>"
                    "<h3 style='color:#00d4ff;margin:0;'>" + s["sector"] + "</h3>"
                    "<p style='margin:0.4rem 0;'>"
                    "Signal: <b style='color:" + s["color"] + ";font-size:1.1rem;'>" + s["signal"] + "</b> | "
                    "Avg Volume: <b>{:.2f}x</b>".format(s["avg_volume_ratio"]) + " | "
                    "30d Change: <b>{:+.2f}%</b>".format(s["avg_price_change"]) + " | "
                    "Stocks: " + str(s["stocks_analyzed"]) + "</p></div>",
                    unsafe_allow_html=True
                )
        else:
            st.info("Sector analysis data not available.")


if __name__ == "__main__":
    st.set_page_config(page_title="Smart Money Tracker", layout="wide")
    show_live_smart_money_tracker()
