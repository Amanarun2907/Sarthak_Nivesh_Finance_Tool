"""IPO Intelligence Hub - Real-time GMP + Full IPO Data from ipowatch.in"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from ipo_live_engine import IPOLiveEngine


# ── Cached data fetchers ──────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def _get_gmp_data():
    """Fetch live GMP data — ipowatch.in → investorgain.com → chittorgarh.com"""
    return IPOLiveEngine().fetch_gmp_ipowatch()


@st.cache_data(ttl=600)
def _get_listed_data():
    """Fetch recently listed IPOs with real listing prices from ipowatch.in"""
    engine = IPOLiveEngine()
    listed = engine.fetch_listed_ipos_ipowatch()
    enriched = engine.get_post_listing_analysis(listed)
    if not enriched and listed:
        basic = []
        for ipo in listed:
            ip = ipo.get("issue_price", 0)
            lp = ipo.get("listing_price", 0)
            gain = ipo.get("listing_gain", 0)
            if ip == 0:
                continue
            if gain >= 20:
                alert, ac, am = "BOOK ALL PROFITS", "#00ff88", f"Strong listing gain {gain:+.1f}%."
            elif gain >= 10:
                alert, ac, am = "BOOK 50% PROFITS", "#17a2b8", f"Good listing gain {gain:+.1f}%."
            elif gain < -5:
                alert, ac, am = "STOP LOSS HIT", "#ff5252", f"Listed below issue price {gain:.1f}%."
            else:
                alert, ac, am = "HOLD", "#ffc107", f"Listing gain {gain:+.1f}%. Monitor."
            basic.append({
                "company": ipo.get("company", ""), "symbol": "SME", "sector": "N/A",
                "issue_price": ip, "listing_price": lp,
                "current_price": lp if lp > 0 else ip,
                "day_high": lp, "day_low": lp, "volume": 0, "avg_volume": 0,
                "volume_ratio": 1, "listing_gain": gain, "total_return": gain,
                "rsi": 50.0, "volatility": 0.0,
                "support": round(ip * 0.90, 2), "resistance": round(ip * 1.30, 2),
                "target_1": round(ip * 1.20, 2), "target_2": round(ip * 1.40, 2),
                "stop_loss": round(ip * 0.90, 2),
                "alert": alert, "alert_color": ac, "alert_msg": am,
                "market_cap": 0, "pe_ratio": 0,
                "week_52_high": 0, "week_52_low": 0,
                "listing_date": ipo.get("listing_date", ""),
                "gmp_at_listing": ipo.get("gmp_at_listing", 0),
            })
        return basic
    return enriched


# ── GMP helper ────────────────────────────────────────────────────────────────

def _gmp_signal(gmp_pct):
    if gmp_pct >= 30:
        return "🔥 VERY STRONG", "#00ff88"
    elif gmp_pct >= 15:
        return "✅ STRONG", "#17a2b8"
    elif gmp_pct >= 5:
        return "🟡 MODERATE", "#ffc107"
    elif gmp_pct > 0:
        return "🟠 WEAK", "#ff9800"
    elif gmp_pct == 0:
        return "⚪ NEUTRAL", "#aaaaaa"
    elif gmp_pct >= -10:
        return "🔴 NEGATIVE", "#ff5252"
    else:
        return "💀 VERY NEGATIVE", "#cc0000"


# ── Main entry point ──────────────────────────────────────────────────────────

def show_ipo_intelligence():
    st.title("🚀 IPO Intelligence Hub")
    st.markdown("""
    <div style='background:linear-gradient(135deg,#0d1117,#161b22);
                border:1px solid #00d4ff;padding:1.2rem;border-radius:12px;margin-bottom:1rem;'>
        <h3 style='color:#00d4ff;margin:0;text-align:center;letter-spacing:2px;'>
            LIVE GMP · REAL-TIME DATA · AI PREDICTIONS · SUBSCRIPTION TRACKER
        </h3>
        <p style='color:#8b949e;margin:0.4rem 0 0 0;text-align:center;font-size:0.85rem;'>
            Sources: ipowatch.in &nbsp;·&nbsp; investorgain.com &nbsp;·&nbsp;
            chittorgarh.com &nbsp;·&nbsp; Yahoo Finance &nbsp;·&nbsp; Google News RSS
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_btn, col_time = st.columns([4, 1])
    with col_btn:
        if st.button("🔄 Refresh All Live Data", type="primary", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with col_time:
        st.caption(f"🕐 {datetime.now().strftime('%d %b %Y  %H:%M:%S')}")

    # Pre-fetch once so all tabs share the same data
    with st.spinner("⚡ Fetching live GMP & IPO data..."):
        all_ipos = _get_gmp_data()

    open_ipos     = [i for i in all_ipos if i["status"] == "Open"]
    upcoming_ipos = [i for i in all_ipos if i["status"] in ["Upcoming", "Unknown"]]

    # Top-level KPI strip
    positive_gmp = sum(1 for i in all_ipos if i.get("gmp", 0) > 0)
    avg_gmp = (sum(i.get("gmp_percent", 0) for i in all_ipos) / len(all_ipos)) if all_ipos else 0
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total IPOs Tracked", len(all_ipos))
    k2.metric("Open Now", len(open_ipos), delta="Live" if open_ipos else None)
    k3.metric("Upcoming", len(upcoming_ipos))
    k4.metric("Positive GMP", f"{positive_gmp}/{len(all_ipos)}")
    k5.metric("Avg GMP", f"{avg_gmp:+.1f}%")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 GMP Dashboard",
        "🟢 Open IPOs",
        "📅 Upcoming Calendar",
        "📈 Listed & Performance",
        "🔔 Exit Alerts",
        "🔍 Allotment Check",
        "📰 IPO News",
    ])

    with tab1:
        _tab_gmp_dashboard(all_ipos)
    with tab2:
        _tab_open_ipos(open_ipos, all_ipos)
    with tab3:
        _tab_upcoming(upcoming_ipos, open_ipos)
    with tab4:
        _tab_listed()
    with tab5:
        _tab_exit_alerts()
    with tab6:
        _tab_allotment()
    with tab7:
        _tab_news(all_ipos)


# ── TAB 1: GMP DASHBOARD ──────────────────────────────────────────────────────

def _tab_gmp_dashboard(all_ipos):
    st.subheader("📊 Real-Time GMP Dashboard")

    if not all_ipos:
        st.error("⚠️ Could not fetch live GMP data from any source (ipowatch.in, investorgain.com, chittorgarh.com). Check internet connection and refresh.")
        return

    source = all_ipos[0].get("source", "ipowatch.in")
    st.success(f"✅ Live GMP data for **{len(all_ipos)} IPOs** — Source: **{source}** — Updated: {datetime.now().strftime('%H:%M:%S')}")

    # ── GMP Cards ────────────────────────────────────────────────────────────
    st.markdown("### 💰 Live GMP Cards")
    cols_per_row = 3
    for i in range(0, len(all_ipos), cols_per_row):
        row_ipos = all_ipos[i:i + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, ipo in zip(cols, row_ipos):
            gmp_val  = ipo.get("gmp", 0)
            gmp_pct  = ipo.get("gmp_percent", 0)
            signal, sig_color = _gmp_signal(gmp_pct)
            est_list = ipo.get("est_listing_price", 0)
            status   = ipo.get("status", "")
            status_badge = (
                "<span style='background:#00ff88;color:#000;padding:2px 8px;"
                "border-radius:4px;font-size:0.7rem;font-weight:bold;'>OPEN</span>"
                if status == "Open" else
                "<span style='background:#ffc107;color:#000;padding:2px 8px;"
                "border-radius:4px;font-size:0.7rem;font-weight:bold;'>UPCOMING</span>"
                if status == "Upcoming" else
                "<span style='background:#555;color:#fff;padding:2px 8px;"
                "border-radius:4px;font-size:0.7rem;'>{}</span>".format(status)
            )
            col.markdown(f"""
            <div style='background:linear-gradient(135deg,#0d1117,#161b22);
                        border:1px solid {sig_color};border-radius:12px;
                        padding:1rem;margin-bottom:0.5rem;'>
                <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
                    <div style='font-size:0.8rem;color:#8b949e;font-weight:600;
                                max-width:70%;line-height:1.3;'>{ipo.get("company","")}</div>
                    {status_badge}
                </div>
                <div style='margin:0.6rem 0;'>
                    <span style='font-size:2rem;font-weight:bold;color:{sig_color};'>
                        ₹{gmp_val:+.0f}
                    </span>
                    <span style='font-size:1rem;color:{sig_color};margin-left:6px;'>
                        ({gmp_pct:+.1f}%)
                    </span>
                </div>
                <div style='font-size:0.85rem;color:{sig_color};font-weight:600;
                            margin-bottom:0.4rem;'>{signal}</div>
                <div style='font-size:0.78rem;color:#8b949e;'>
                    Price Band: <b style='color:#e6edf3;'>{ipo.get("price_band","N/A")}</b>
                </div>
                <div style='font-size:0.78rem;color:#8b949e;'>
                    Est. Listing: <b style='color:#e6edf3;'>
                        {"₹{:.0f}".format(est_list) if est_list > 0 else "N/A"}
                    </b>
                </div>
                <div style='font-size:0.75rem;color:#555;margin-top:0.3rem;'>
                    {ipo.get("open_date","") + " → " + ipo.get("close_date","") if ipo.get("open_date") else ""}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── GMP Bar Chart ─────────────────────────────────────────────────────────
    st.markdown("### 📈 GMP % Comparison — All IPOs")
    sorted_ipos = sorted(all_ipos, key=lambda x: x.get("gmp_percent", 0), reverse=True)
    names  = [i["company"][:22] for i in sorted_ipos]
    gmps   = [i.get("gmp_percent", 0) for i in sorted_ipos]
    colors = [_gmp_signal(g)[1] for g in gmps]
    fig = go.Figure(go.Bar(
        x=names, y=gmps, marker_color=colors,
        text=[f"{g:+.1f}%" for g in gmps], textposition="outside",
        hovertemplate="<b>%{x}</b><br>GMP: %{y:+.1f}%<extra></extra>"
    ))
    fig.update_layout(
        title="Live Grey Market Premium % — Sorted High to Low",
        yaxis_title="GMP %", xaxis_tickangle=-35,
        template="plotly_dark", height=420,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(b=100)
    )
    fig.add_hline(y=0, line_dash="dash", line_color="#555")
    st.plotly_chart(fig, use_container_width=True)

    # ── GMP vs Est. Listing Price scatter ─────────────────────────────────────
    scatter_ipos = [i for i in all_ipos if i.get("issue_price", 0) > 0 and i.get("est_listing_price", 0) > 0]
    if scatter_ipos:
        st.markdown("### 🎯 Issue Price vs Estimated Listing Price")
        fig2 = go.Figure()
        for ipo in scatter_ipos:
            ip  = ipo.get("issue_price", 0)
            elp = ipo.get("est_listing_price", 0)
            gp  = ipo.get("gmp_percent", 0)
            _, sc = _gmp_signal(gp)
            fig2.add_trace(go.Scatter(
                x=[ip], y=[elp],
                mode="markers+text",
                marker=dict(size=14, color=sc, line=dict(width=1, color="#fff")),
                text=[ipo["company"][:15]],
                textposition="top center",
                textfont=dict(size=9, color="#e6edf3"),
                name=ipo["company"][:20],
                hovertemplate=(
                    f"<b>{ipo['company']}</b><br>"
                    f"Issue Price: ₹{ip:.0f}<br>"
                    f"Est. Listing: ₹{elp:.0f}<br>"
                    f"GMP: {gp:+.1f}%<extra></extra>"
                )
            ))
        # diagonal reference line
        all_prices = [i.get("issue_price", 0) for i in scatter_ipos]
        mn, mx = min(all_prices) * 0.9, max(all_prices) * 1.1
        fig2.add_trace(go.Scatter(
            x=[mn, mx], y=[mn, mx],
            mode="lines", line=dict(dash="dash", color="#555", width=1),
            name="No Gain Line", showlegend=False
        ))
        fig2.update_layout(
            title="Issue Price vs Estimated Listing Price (dot above line = positive GMP)",
            xaxis_title="Issue Price (₹)", yaxis_title="Est. Listing Price (₹)",
            template="plotly_dark", height=420, showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── GMP Accuracy vs Listed IPOs ───────────────────────────────────────────
    st.markdown("### 🏆 GMP Accuracy Tracker — How Accurate Was GMP?")
    listed_raw = IPOLiveEngine().fetch_listed_ipos_ipowatch()
    accuracy_rows = [
        l for l in listed_raw
        if l.get("issue_price", 0) > 0
        and l.get("listing_price", 0) > 0
        and l.get("gmp_at_listing", 0) != 0
    ]
    if accuracy_rows:
        acc_names, gmp_pred, actual_gain = [], [], []
        for l in accuracy_rows[:15]:
            ip = l["issue_price"]
            lp = l["listing_price"]
            gmp = l.get("gmp_at_listing", 0)
            gmp_pct_pred = round((gmp / ip) * 100, 1) if ip > 0 else 0
            actual = round(((lp - ip) / ip) * 100, 1)
            acc_names.append(l["company"][:18])
            gmp_pred.append(gmp_pct_pred)
            actual_gain.append(actual)
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            name="GMP Predicted %", x=acc_names, y=gmp_pred,
            marker_color="#00d4ff",
            text=[f"{g:+.1f}%" for g in gmp_pred], textposition="outside"
        ))
        fig3.add_trace(go.Bar(
            name="Actual Listing Gain %", x=acc_names, y=actual_gain,
            marker_color="#00ff88",
            text=[f"{g:+.1f}%" for g in actual_gain], textposition="outside"
        ))
        fig3.update_layout(
            title="GMP Prediction vs Actual Listing Gain (Real Data)",
            barmode="group", yaxis_title="%",
            template="plotly_dark", height=400,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis_tickangle=-30
        )
        st.plotly_chart(fig3, use_container_width=True)
        # accuracy score
        correct = sum(1 for p, a in zip(gmp_pred, actual_gain)
                      if (p > 0 and a > 0) or (p < 0 and a < 0))
        if gmp_pred:
            st.info(f"📐 GMP Direction Accuracy: **{correct}/{len(gmp_pred)}** "
                    f"({correct/len(gmp_pred)*100:.0f}%) — based on real listing data from ipowatch.in")
    else:
        st.caption("GMP accuracy data will appear once IPOs with both GMP and listing price data are available.")

    # ── Full GMP Table ────────────────────────────────────────────────────────
    st.markdown("### 📋 Complete GMP Data Table")
    rows = []
    for ipo in sorted_ipos:
        gmp = ipo.get("gmp", 0)
        gmp_pct = ipo.get("gmp_percent", 0)
        signal, _ = _gmp_signal(gmp_pct)
        rows.append({
            "IPO Name":       ipo.get("company", ""),
            "Status":         ipo.get("status", ""),
            "Price Band":     ipo.get("price_band", ""),
            "Issue Price":    f"₹{ipo.get('issue_price',0):.0f}" if ipo.get("issue_price", 0) > 0 else "N/A",
            "GMP (₹)":        f"₹{gmp:+.0f}",
            "GMP %":          f"{gmp_pct:+.1f}%",
            "Est. Listing ₹": f"₹{ipo.get('est_listing_price',0):.0f}" if ipo.get("est_listing_price", 0) > 0 else "N/A",
            "Signal":         signal,
            "Open Date":      ipo.get("open_date", ""),
            "Close Date":     ipo.get("close_date", ""),
            "Source":         ipo.get("source", ""),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, height=480)
    st.caption("⚠️ GMP is unofficial grey market data. Indicative only. Not financial advice.")


# ── TAB 2: OPEN IPOs ──────────────────────────────────────────────────────────

def _tab_open_ipos(open_ipos, all_ipos):
    st.subheader("🟢 Currently Open IPOs — Apply or Avoid?")

    if not open_ipos:
        st.info("ℹ️ No IPOs currently open for subscription.")
        upcoming = [i for i in all_ipos if i["status"] == "Upcoming"]
        if upcoming:
            st.markdown("### 🔜 Opening Soon")
            for u in upcoming[:5]:
                _, sc = _gmp_signal(u.get("gmp_percent", 0))
                st.markdown(
                    f"**{u['company']}** — Opens: {u.get('open_date','?')} | "
                    f"Price: {u.get('price_band','N/A')} | "
                    f"GMP: <span style='color:{sc};'>₹{u.get('gmp',0):+.0f} "
                    f"({u.get('gmp_percent',0):+.1f}%)</span>",
                    unsafe_allow_html=True
                )
        return

    st.success(f"✅ {len(open_ipos)} IPO(s) currently open for subscription")
    engine = IPOLiveEngine()

    for ipo in open_ipos:
        company  = ipo.get("company", "N/A")
        gmp_val  = ipo.get("gmp", 0)
        gmp_pct  = ipo.get("gmp_percent", 0)
        signal, sig_color = _gmp_signal(gmp_pct)
        est_list = ipo.get("est_listing_price", 0)

        with st.expander(
            f"🏢 {company}  |  {ipo.get('price_band','N/A')}  |  "
            f"GMP: ₹{gmp_val:+.0f} ({gmp_pct:+.1f}%)  |  {signal}",
            expanded=True
        ):
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Price Band",   ipo.get("price_band", "N/A"))
            c2.metric("Open Date",    ipo.get("open_date", "N/A"))
            c3.metric("Close Date",   ipo.get("close_date", "N/A"))
            c4.metric("GMP",          f"₹{gmp_val:+.0f}", f"{gmp_pct:+.1f}%")
            c5.metric("Est. Listing", f"₹{est_list:.0f}" if est_list > 0 else "N/A")

            st.markdown(f"""
            <div style='background:rgba(0,0,0,0.35);padding:0.9rem;border-radius:10px;
                        border-left:5px solid {sig_color};margin:0.6rem 0;'>
                <span style='color:{sig_color};font-size:1.1rem;font-weight:bold;'>
                    {signal} &nbsp; GMP: ₹{gmp_val:+.0f} ({gmp_pct:+.1f}%)
                </span><br>
                <span style='color:#e6edf3;font-size:0.9rem;'>
                    Estimated Listing Price: <b>₹{est_list:.0f}</b>
                    &nbsp;|&nbsp; Source: <i>{ipo.get("source","ipowatch.in")} (live)</i>
                </span>
            </div>
            """, unsafe_allow_html=True)

            # Subscription
            with st.spinner("Fetching live subscription data..."):
                sub = engine.fetch_subscription_data(company)
            if sub["total"] > 0 or sub["qib"] > 0:
                st.markdown("**📊 Live Subscription Status**")
                sc1, sc2, sc3, sc4, sc5 = st.columns(5)
                sc1.metric("QIB",      f"{sub['qib']:.1f}x")
                sc2.metric("HNI/NII",  f"{sub['hni']:.1f}x")
                sc3.metric("Retail",   f"{sub['retail']:.1f}x")
                sc4.metric("Employee", f"{sub['employee']:.1f}x")
                sc5.metric("Total",    f"{sub['total']:.1f}x",
                           delta="Oversubscribed" if sub["total"] > 1 else "Undersubscribed")
            else:
                st.caption("📊 Subscription data not yet available")

            # AI Prediction
            with st.spinner("Running AI prediction..."):
                pred = engine.predict_listing_gain(ipo)
            pred_color = pred["color"]
            st.markdown(f"""
            <div style='background:rgba(0,0,0,0.4);padding:1.2rem;border-radius:10px;
                        border:2px solid {pred_color};margin:0.8rem 0;'>
                <h3 style='color:{pred_color};margin:0;'>
                    🤖 AI: {pred["recommendation"]} &nbsp; Confidence: {pred["confidence"]}%
                </h3>
                <p style='margin:0.5rem 0;color:#e0e0e0;'>
                    Est. Gain: <b style='color:{pred_color};'>{pred["est_listing_gain"]:+.1f}%</b>
                    &nbsp;|&nbsp; Est. Listing: <b>₹{pred["est_listing_price"]:.0f}</b>
                    &nbsp;|&nbsp; Stop Loss: <b style='color:#ff5252;'>₹{pred["stop_loss"]:.0f}</b>
                    &nbsp;|&nbsp; Score: <b>{pred["score"]}/100</b>
                </p>
            </div>
            """, unsafe_allow_html=True)

            if pred["signals"]:
                st.markdown("**Key Signals:**")
                for sig in pred["signals"]:
                    icon = "✅" if any(w in sig.lower() for w in ["strong", "exceptional", "mega", "massive"]) else "📌"
                    st.markdown(f"{icon} {sig}")

            # News
            with st.spinner("Fetching news..."):
                news = engine.fetch_ipo_news(company)
            if news.get("news"):
                label = news.get("label", "Neutral")
                nc_label = "🟢" if label == "Positive" else "🔴" if label == "Negative" else "🟡"
                st.markdown(f"**📰 News: {nc_label} {label} (score: {news.get('avg_sentiment',0):.2f})**")
                for n in news["news"][:4]:
                    nc = "#00ff88" if n["sentiment"] > 0.1 else "#ff5252" if n["sentiment"] < -0.1 else "#aaa"
                    st.markdown(
                        f"<small style='color:{nc};'>● {n['title']} — <i>{n['source']}</i></small>",
                        unsafe_allow_html=True
                    )


# ── TAB 3: UPCOMING CALENDAR ──────────────────────────────────────────────────

def _tab_upcoming(upcoming_ipos, open_ipos):
    st.subheader("📅 Upcoming IPO Calendar")
    all_show = open_ipos + upcoming_ipos
    if not all_show:
        st.info("No upcoming IPO data available right now.")
        return

    st.success(f"Found {len(all_show)} IPO(s) in pipeline")

    rows = []
    for ipo in all_show:
        gmp     = ipo.get("gmp", 0)
        gmp_pct = ipo.get("gmp_percent", 0)
        signal, _ = _gmp_signal(gmp_pct)
        rows.append({
            "Company":      ipo.get("company", ""),
            "Status":       ipo.get("status", ""),
            "Open Date":    ipo.get("open_date", ""),
            "Close Date":   ipo.get("close_date", ""),
            "Price Band":   ipo.get("price_band", ""),
            "GMP (₹)":      f"₹{gmp:+.0f}",
            "GMP %":        f"{gmp_pct:+.1f}%",
            "Est. Listing": f"₹{ipo.get('est_listing_price',0):.0f}" if ipo.get("est_listing_price", 0) > 0 else "N/A",
            "Signal":       signal,
            "Source":       ipo.get("source", ""),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, height=420)

    # GMP bar chart
    names  = [r["Company"][:22] for r in rows]
    gmps   = [ipo.get("gmp_percent", 0) for ipo in all_show]
    colors = [_gmp_signal(g)[1] for g in gmps]
    fig = go.Figure(go.Bar(
        x=names, y=gmps, marker_color=colors,
        text=[f"{g:+.1f}%" for g in gmps], textposition="outside",
        hovertemplate="<b>%{x}</b><br>GMP: %{y:+.1f}%<extra></extra>"
    ))
    fig.update_layout(
        title="GMP % — Upcoming & Open IPOs (Live from ipowatch.in)",
        yaxis_title="GMP %", xaxis_tickangle=-30,
        template="plotly_dark", height=380,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )
    fig.add_hline(y=0, line_dash="dash", line_color="#555")
    st.plotly_chart(fig, use_container_width=True)


# ── TAB 4: LISTED & PERFORMANCE ───────────────────────────────────────────────

def _tab_listed():
    st.subheader("📈 Recently Listed IPOs — Live Performance")
    with st.spinner("Fetching listed IPOs and live prices..."):
        enriched = _get_listed_data()
    if not enriched:
        st.warning("Could not fetch listed IPO performance data right now.")
        return

    avg_ret    = sum(e["total_return"] for e in enriched) / len(enriched)
    profitable = sum(1 for e in enriched if e["total_return"] > 0)
    best       = max(enriched, key=lambda x: x["total_return"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("IPOs Tracked",   len(enriched))
    c2.metric("Avg Return",     f"{avg_ret:+.1f}%")
    c3.metric("Profitable",     f"{profitable}/{len(enriched)}")
    c4.metric("Best Performer", best["company"][:16], f"{best['total_return']:+.1f}%")

    companies     = [e["company"][:16] for e in enriched]
    listing_gains = [e["listing_gain"] for e in enriched]
    total_returns = [e["total_return"] for e in enriched]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Listing Day Gain", x=companies, y=listing_gains,
        marker_color="#00d4ff",
        text=[f"{g:+.1f}%" for g in listing_gains], textposition="outside"
    ))
    fig.add_trace(go.Bar(
        name="Current Total Return", x=companies, y=total_returns,
        marker_color="#00ff88",
        text=[f"{g:+.1f}%" for g in total_returns], textposition="outside"
    ))
    fig.update_layout(
        title="IPO Performance — Real-time (Yahoo Finance + ipowatch.in)",
        barmode="group", template="plotly_dark", height=420,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=True)

    for e in enriched:
        ac = e["alert_color"]
        with st.expander(
            f"🏢 {e['company']} ({e['symbol']})  |  {e['alert']}  |  {e['total_return']:+.1f}%"
        ):
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Issue Price",   f"₹{e['issue_price']:.0f}")
            c2.metric("Listing Price", f"₹{e['listing_price']:.0f}", f"{e['listing_gain']:+.1f}%")
            c3.metric("Current Price", f"₹{e['current_price']:.2f}", f"{e['total_return']:+.1f}%")
            c4.metric("RSI",           f"{e['rsi']:.0f}")
            c5.metric("Volume",        f"{e['volume_ratio']:.1f}x avg")
            st.markdown(f"""
            <div style='background:rgba(0,0,0,0.3);padding:0.8rem;border-radius:8px;
                        border-left:4px solid {ac};margin:0.5rem 0;'>
                <b style='color:{ac};'>{e["alert"]}</b> — {e["alert_msg"]}
            </div>
            """, unsafe_allow_html=True)
            tc1, tc2, tc3, tc4 = st.columns(4)
            tc1.info(f"Support: ₹{e['support']:.2f}")
            tc2.success(f"Target 1: ₹{e['target_1']:.2f}")
            tc3.success(f"Target 2: ₹{e['target_2']:.2f}")
            tc4.error(f"Stop Loss: ₹{e['stop_loss']:.2f}")
            if e.get("week_52_high", 0) > 0:
                st.caption(
                    f"52W: ₹{e['week_52_low']:.2f} – ₹{e['week_52_high']:.2f}  "
                    f"|  Sector: {e['sector']}  |  P/E: {e['pe_ratio']:.1f}"
                )


# ── TAB 5: EXIT ALERTS ────────────────────────────────────────────────────────

def _tab_exit_alerts():
    st.subheader("🔔 Real-time Exit Alerts — Listed IPOs")
    st.info("Live monitoring of listed IPOs. Alerts triggered when targets or stop-losses are hit.")
    with st.spinner("Loading live exit alerts..."):
        enriched = _get_listed_data()
    if not enriched:
        st.warning("No post-listing data available right now.")
        return

    alerts_triggered = [e for e in enriched if e["alert"] in
                        ["BOOK ALL PROFITS", "BOOK 50% PROFITS", "STOP LOSS HIT"]]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("IPOs Monitored", len(enriched))
    c2.metric("Active Alerts",  len(alerts_triggered))
    c3.metric("Avg Return",     f"{sum(e['total_return'] for e in enriched)/len(enriched):+.1f}%")
    c4.metric("Win Rate",       f"{sum(1 for e in enriched if e['total_return'] > 0)}/{len(enriched)}")

    st.markdown("---")
    priority = {"STOP LOSS HIT": 0, "BOOK ALL PROFITS": 1, "BOOK 50% PROFITS": 2,
                "REVIEW POSITION": 3, "HOLD - TRAIL SL": 4, "HOLD": 5}
    for e in sorted(enriched, key=lambda x: priority.get(x["alert"], 9)):
        ac = e["alert_color"]
        st.markdown(f"""
        <div style='background:rgba(0,0,0,0.3);padding:1rem;border-radius:10px;
                    border-left:5px solid {ac};margin:0.5rem 0;'>
            <div style='display:flex;justify-content:space-between;align-items:center;'>
                <div>
                    <b style='color:{ac};font-size:1.05rem;'>{e["alert"]}</b>
                    &nbsp;—&nbsp; <b>{e["company"]}</b>
                    &nbsp;<small style='color:#aaa;'>({e["symbol"]})</small><br>
                    <small style='color:#ccc;'>{e["alert_msg"]}</small>
                </div>
                <div style='text-align:right;min-width:100px;'>
                    <b style='color:{ac};font-size:1.4rem;'>{e["total_return"]:+.1f}%</b><br>
                    <small style='color:#aaa;'>₹{e["current_price"]:.2f}</small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── TAB 6: ALLOTMENT CHECK ────────────────────────────────────────────────────

def _tab_allotment():
    st.subheader("🔍 IPO Allotment Status Checker")
    st.info("Enter your PAN to check allotment status via official registrar links.")
    with st.form("allotment_form"):
        pan     = st.text_input("PAN Number", placeholder="ABCDE1234F", max_chars=10)
        company = st.text_input("IPO Company Name (optional)", placeholder="e.g. Hyundai India")
        submitted = st.form_submit_button("Check Allotment", type="primary")

    if submitted:
        if not pan or len(pan) != 10:
            st.error("Please enter a valid 10-character PAN number.")
        else:
            result = IPOLiveEngine().check_allotment_status(pan.upper(), company)
            st.markdown(f"""
            <div style='background:rgba(0,0,0,0.3);padding:1.2rem;border-radius:10px;
                        border-left:5px solid #00d4ff;'>
                <h4 style='color:#00d4ff;'>PAN: {result["pan"]}</h4>
                <p>{result["note"]}</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("### Official Registrar Links")
            for name, (url, ipos_handled) in result["registrars"].items():
                st.markdown(f"**[{name}]({url})** — Handles: {ipos_handled}")

    st.markdown("---")
    st.markdown("""
    ### How to Check Allotment
    1. Go to the registrar website for your IPO
    2. Select the IPO name from the dropdown
    3. Enter your PAN or Application number
    4. Click Submit

    **Allotment Timeline:**
    - IPO closes → T+6 days: Allotment finalized
    - T+7 days: Listing on NSE/BSE
    - Refunds credited within T+6 days
    """)


# ── TAB 7: IPO NEWS ───────────────────────────────────────────────────────────

def _tab_news(all_ipos):
    st.subheader("📰 Live IPO News & Sentiment")
    if not all_ipos:
        st.info("No IPO data available to fetch news for.")
        return

    engine = IPOLiveEngine()
    # Let user pick which IPO to get news for
    company_names = [i["company"] for i in all_ipos]
    selected = st.selectbox("Select IPO for news", company_names)

    if selected:
        with st.spinner(f"Fetching live news for {selected}..."):
            news_data = engine.fetch_ipo_news(selected)

        label = news_data.get("label", "Neutral")
        avg_s = news_data.get("avg_sentiment", 0)
        articles = news_data.get("news", [])

        label_color = "#00ff88" if label == "Positive" else "#ff5252" if label == "Negative" else "#ffc107"
        label_icon  = "🟢" if label == "Positive" else "🔴" if label == "Negative" else "🟡"

        st.markdown(f"""
        <div style='background:rgba(0,0,0,0.3);padding:1rem;border-radius:10px;
                    border-left:5px solid {label_color};margin-bottom:1rem;'>
            <h4 style='color:{label_color};margin:0;'>
                {label_icon} News Sentiment: {label}
                &nbsp;|&nbsp; Score: {avg_s:.2f}
                &nbsp;|&nbsp; {len(articles)} articles found
            </h4>
        </div>
        """, unsafe_allow_html=True)

        if articles:
            for n in articles:
                s = n.get("sentiment", 0)
                nc = "#00ff88" if s > 0.1 else "#ff5252" if s < -0.1 else "#aaa"
                icon = "📈" if s > 0.1 else "📉" if s < -0.1 else "📰"
                st.markdown(
                    f"<div style='padding:0.4rem 0;border-bottom:1px solid #222;'>"
                    f"{icon} <span style='color:{nc};'>{n.get('title','')}</span>"
                    f" &nbsp;<small style='color:#555;'>— {n.get('source','')}</small>"
                    f"</div>",
                    unsafe_allow_html=True
                )
        else:
            st.caption("No news articles found for this IPO right now.")

    # Bulk sentiment overview
    st.markdown("---")
    st.markdown("### 📊 Sentiment Overview — All IPOs")
    st.caption("Fetching news for all IPOs may take a moment...")
    if st.button("Load Sentiment for All IPOs"):
        sentiment_rows = []
        prog = st.progress(0)
        for idx, ipo in enumerate(all_ipos):
            nd = engine.fetch_ipo_news(ipo["company"])
            sentiment_rows.append({
                "IPO":       ipo["company"],
                "Sentiment": nd.get("label", "Neutral"),
                "Score":     round(nd.get("avg_sentiment", 0), 3),
                "Articles":  len(nd.get("news", [])),
            })
            prog.progress((idx + 1) / len(all_ipos))
        prog.empty()
        df_sent = pd.DataFrame(sentiment_rows)
        st.dataframe(df_sent, use_container_width=True)
        scores = df_sent["Score"].tolist()
        names  = df_sent["IPO"].tolist()
        colors = ["#00ff88" if s > 0.1 else "#ff5252" if s < -0.1 else "#aaa" for s in scores]
        fig = go.Figure(go.Bar(
            x=[n[:20] for n in names], y=scores,
            marker_color=colors,
            text=[f"{s:.2f}" for s in scores], textposition="outside"
        ))
        fig.update_layout(
            title="News Sentiment Score per IPO (Live)",
            yaxis_title="Sentiment Score", template="plotly_dark", height=380,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
        )
        fig.add_hline(y=0, line_dash="dash", line_color="#555")
        st.plotly_chart(fig, use_container_width=True)
