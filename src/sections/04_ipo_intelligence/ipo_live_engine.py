"""IPO Live Engine - 100% Real Data from Verified Working Sources"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import re
import time
from textblob import TextBlob


class IPOLiveEngine:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        })

    def _get(self, url, timeout=15):
        r = self.session.get(url, timeout=timeout)
        r.encoding = "utf-8"
        return r

    def _get_status(self, open_str, close_str):
        today = datetime.now()
        for fmt in ["%d %b %Y", "%d-%b-%Y", "%d/%m/%Y", "%Y-%m-%d",
                    "%d %B %Y", "%b %d, %Y", "%d-%m-%Y"]:
            try:
                o = datetime.strptime(open_str.strip(), fmt)
                c = datetime.strptime(close_str.strip(), fmt)
                if today < o:
                    return "Upcoming"
                elif o <= today <= c:
                    return "Open"
                else:
                    return "Closed"
            except:
                continue
        return "Unknown"

    def _parse_price(self, price_str):
        try:
            nums = re.findall(r"\d+", str(price_str).replace(",", ""))
            return float(nums[-1]) if nums else 0
        except:
            return 0

    # ── SOURCE 1: LIVE GMP (ipowatch → investorgain → chittorgarh) ──────────
    def fetch_gmp_ipowatch(self):
        """Fetch GMP from live sources only. Returns empty list if all fail."""
        ipos = self._fetch_ipowatch_primary()
        if ipos:
            return ipos
        print("ipowatch.in failed, trying investorgain.com...")
        ipos = self._fetch_investorgain()
        if ipos:
            return ipos
        print("investorgain.com failed, trying chittorgarh.com...")
        ipos = self._fetch_chittorgarh()
        if ipos:
            return ipos
        print("All live GMP sources unavailable.")
        return []

    def _fetch_ipowatch_primary(self):
        """
        Scrapes ipowatch.in/upcoming-ipo/ for real Open/Upcoming IPOs with dates,
        then merges GMP values from the GMP page by company name matching.
        Only returns IPOs that are genuinely Open or Upcoming (not historical).
        """
        ipos = []
        try:
            hdrs = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Referer": "https://www.google.com/",
            }

            # ── STEP 1: Fetch GMP lookup dict from GMP page ──────────────────
            gmp_lookup = {}  # company_name_lower → gmp_val
            try:
                rg = requests.get(
                    "https://ipowatch.in/ipo-grey-market-premium-latest-ipo-gmp/",
                    headers=hdrs, timeout=15
                )
                sg = BeautifulSoup(rg.text, "html.parser")
                tables_g = sg.find_all("table")
                target_g = max(tables_g, key=lambda t: len(t.find_all("tr"))) if tables_g else None
                if target_g:
                    for row in target_g.find_all("tr")[1:]:
                        cols = row.find_all("td")
                        if len(cols) < 3:
                            continue
                        name = cols[0].get_text(strip=True).lower().strip()
                        gmp_nums = re.findall(r"[-+]?\d+\.?\d*", cols[2].get_text(strip=True).replace(",", ""))
                        if name and gmp_nums:
                            gmp_lookup[name] = float(gmp_nums[0])
            except Exception as e:
                print(f"GMP lookup error: {e}")

            # ── STEP 2: Fetch upcoming/open IPOs from upcoming page ───────────
            ru = requests.get("https://ipowatch.in/upcoming-ipo/", headers=hdrs, timeout=15)
            ru.encoding = "utf-8"
            su = BeautifulSoup(ru.text, "html.parser")
            tables_u = su.find_all("table")

            year = datetime.now().year

            for table in tables_u:
                rows = table.find_all("tr")
                if len(rows) < 2:
                    continue
                header_cols = [c.get_text(strip=True).lower() for c in rows[0].find_all(["td", "th"])]
                # Must have company + date columns
                if not any("company" in h or "ipo" in h for h in header_cols):
                    continue

                for row in rows[1:]:
                    cols = row.find_all(["td", "th"])
                    if len(cols) < 2:
                        continue
                    try:
                        company = cols[0].get_text(strip=True)
                        if not company or company.lower() in ["company", "ipo", ""]:
                            continue

                        date_text = cols[1].get_text(strip=True) if len(cols) > 1 else ""
                        price_band = cols[3].get_text(strip=True) if len(cols) > 3 else ""

                        # Parse price band → issue price (upper end)
                        price_nums = re.findall(r"\d+\.?\d*", price_band.replace(",", ""))
                        issue_price = float(price_nums[-1]) if price_nums else 0

                        # Parse date range like "10-16 April" or "6-8 April"
                        open_date, close_date = self._parse_date_range_with_year(date_text, year)
                        status = self._get_status(open_date, close_date) if open_date else "Unknown"

                        # Skip purely future 2026/2027 placeholders with no real date
                        if date_text.strip() in ["2026", "2027", "TBA", ""]:
                            continue

                        # Only include Open or Upcoming (not Closed/Listed)
                        if status == "Closed":
                            continue

                        # GMP lookup by fuzzy company name match
                        gmp_val = 0.0
                        company_lower = company.lower().strip()
                        # exact match first
                        if company_lower in gmp_lookup:
                            gmp_val = gmp_lookup[company_lower]
                        else:
                            # partial match — first word
                            first_word = company_lower.split()[0] if company_lower.split() else ""
                            for k, v in gmp_lookup.items():
                                if first_word and first_word in k:
                                    gmp_val = v
                                    break

                        gmp_pct = round((gmp_val / issue_price) * 100, 2) if issue_price > 0 else 0
                        est_listing = round(issue_price + gmp_val, 2) if issue_price > 0 else 0

                        ipos.append({
                            "company": company,
                            "gmp": gmp_val,
                            "gmp_percent": gmp_pct,
                            "price_band": price_band,
                            "issue_price": issue_price,
                            "listing_price": 0,
                            "est_listing_price": est_listing,
                            "listing_gain_text": f"{gmp_pct:+.1f}%",
                            "date_range": date_text,
                            "open_date": open_date,
                            "close_date": close_date,
                            "status": status,
                            "signal": "Positive" if gmp_val > 0 else "Negative" if gmp_val < 0 else "Neutral",
                            "source": "ipowatch.in"
                        })
                    except:
                        continue

        except Exception as e:
            print(f"ipowatch.in upcoming error: {e}")

        # Deduplicate by company name
        seen = set()
        unique = []
        for ipo in ipos:
            key = ipo["company"].lower().strip()
            if key not in seen:
                seen.add(key)
                unique.append(ipo)

        # Sort: Open first, then Upcoming
        order = {"Open": 0, "Upcoming": 1, "Unknown": 2}
        unique.sort(key=lambda x: order.get(x["status"], 3))
        return unique

    def _parse_date_range_with_year(self, date_str, year):
        """Parse '10-16 April', '6-8 April 2026', '27-8 April' etc."""
        try:
            date_str = date_str.strip()
            # Pattern: "10-16 April" or "10-16 April 2026"
            m = re.match(r"(\d+)-(\d+)\s+([A-Za-z]+)(?:\s+(\d{4}))?", date_str)
            if m:
                d1, d2, mon, yr = m.group(1), m.group(2), m.group(3), m.group(4) or str(year)
                return f"{d1} {mon} {yr}", f"{d2} {mon} {yr}"
            # Pattern: "27-8 April" (cross-month edge case — treat same month)
            m2 = re.match(r"(\d+)\s+([A-Za-z]+)\s*-\s*(\d+)\s+([A-Za-z]+)(?:\s+(\d{4}))?", date_str)
            if m2:
                d1, mon1, d2, mon2, yr = m2.group(1), m2.group(2), m2.group(3), m2.group(4), m2.group(5) or str(year)
                return f"{d1} {mon1} {yr}", f"{d2} {mon2} {yr}"
        except:
            pass
        return "", ""

    def _fetch_investorgain(self):
        """Fallback 1: investorgain.com GMP table"""
        ipos = []
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Referer": "https://www.google.com/"
            }
            r = requests.get("https://www.investorgain.com/report/live-ipo-gmp/331/", headers=headers, timeout=15)
            r.encoding = "utf-8"
            soup = BeautifulSoup(r.text, "html.parser")
            table = soup.find("table", {"id": "mainTable"}) or soup.find("table")
            if not table:
                return []
            for row in table.find_all("tr")[1:]:
                cols = row.find_all("td")
                if len(cols) < 4:
                    continue
                try:
                    company = cols[0].get_text(strip=True)
                    if not company:
                        continue
                    price_text = cols[1].get_text(strip=True)
                    gmp_text = cols[2].get_text(strip=True)
                    gain_text = cols[3].get_text(strip=True)
                    date_text = cols[4].get_text(strip=True) if len(cols) > 4 else ""
                    price_nums = re.findall(r"\d+", price_text.replace(",", ""))
                    issue_price = float(price_nums[-1]) if price_nums else 0
                    gmp_nums = re.findall(r"[-+]?\d+\.?\d*", gmp_text.replace(",", ""))
                    gmp_val = float(gmp_nums[0]) if gmp_nums else 0
                    gain_nums = re.findall(r"[-+]?\d+\.?\d*", gain_text)
                    gain_pct = float(gain_nums[0]) if gain_nums else 0
                    gmp_pct = round((gmp_val / issue_price) * 100, 2) if issue_price > 0 else gain_pct
                    est_listing = round(issue_price + gmp_val, 2) if issue_price > 0 else 0
                    open_date, close_date = self._parse_date_range(date_text)
                    status = self._get_status(open_date, close_date) if open_date else "Unknown"
                    ipos.append({
                        "company": company, "gmp": gmp_val, "gmp_percent": gmp_pct,
                        "price_band": price_text, "issue_price": issue_price,
                        "est_listing_price": est_listing, "listing_gain_text": gain_text,
                        "date_range": date_text, "open_date": open_date, "close_date": close_date,
                        "status": status,
                        "signal": "Positive" if gmp_val > 0 else "Negative" if gmp_val < 0 else "Neutral",
                        "source": "investorgain.com"
                    })
                except:
                    continue
        except Exception as e:
            print(f"investorgain.com error: {e}")
        return ipos

    def _fetch_chittorgarh(self):
        """Fallback 2: chittorgarh.com IPO GMP page"""
        ipos = []
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Referer": "https://www.google.com/"
            }
            r = requests.get("https://www.chittorgarh.com/report/ipo-grey-market-premium-gmp-today/93/", headers=headers, timeout=15)
            r.encoding = "utf-8"
            soup = BeautifulSoup(r.text, "html.parser")
            table = soup.find("table")
            if not table:
                return []
            for row in table.find_all("tr")[1:]:
                cols = row.find_all("td")
                if len(cols) < 3:
                    continue
                try:
                    company = cols[0].get_text(strip=True)
                    if not company:
                        continue
                    price_text = cols[1].get_text(strip=True) if len(cols) > 1 else "0"
                    gmp_text = cols[2].get_text(strip=True) if len(cols) > 2 else "0"
                    gain_text = cols[3].get_text(strip=True) if len(cols) > 3 else "0"
                    price_nums = re.findall(r"\d+", price_text.replace(",", ""))
                    issue_price = float(price_nums[-1]) if price_nums else 0
                    gmp_nums = re.findall(r"[-+]?\d+\.?\d*", gmp_text.replace(",", ""))
                    gmp_val = float(gmp_nums[0]) if gmp_nums else 0
                    gain_nums = re.findall(r"[-+]?\d+\.?\d*", gain_text)
                    gain_pct = float(gain_nums[0]) if gain_nums else 0
                    gmp_pct = round((gmp_val / issue_price) * 100, 2) if issue_price > 0 else gain_pct
                    est_listing = round(issue_price + gmp_val, 2) if issue_price > 0 else 0
                    ipos.append({
                        "company": company, "gmp": gmp_val, "gmp_percent": gmp_pct,
                        "price_band": price_text, "issue_price": issue_price,
                        "est_listing_price": est_listing, "listing_gain_text": gain_text,
                        "date_range": "", "open_date": "", "close_date": "",
                        "status": "Unknown",
                        "signal": "Positive" if gmp_val > 0 else "Negative" if gmp_val < 0 else "Neutral",
                        "source": "chittorgarh.com"
                    })
                except:
                    continue
        except Exception as e:
            print(f"chittorgarh.com error: {e}")
        return ipos

    def _parse_date_range(self, date_str):
        """Wrapper kept for backward compatibility."""
        return self._parse_date_range_with_year(date_str, datetime.now().year)

    # ── SOURCE 2: IPOWATCH.IN LISTED IPOs ────────────────────────────────────
    def fetch_listed_ipos_ipowatch(self):
        """
        Fetch recently listed IPOs directly from the GMP page.
        Columns: IPO Name | Issue Price | GMP | Listing Price
        Only returns rows where a real listing price exists.
        Returns most recent 20.
        """
        listed = []
        try:
            hdrs = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Referer": "https://www.google.com/",
            }
            r = requests.get(
                "https://ipowatch.in/ipo-grey-market-premium-latest-ipo-gmp/",
                headers=hdrs, timeout=15
            )
            r.encoding = "utf-8"
            soup = BeautifulSoup(r.text, "html.parser")
            tables = soup.find_all("table")
            if not tables:
                return []
            # Largest table = GMP tracker with all listed IPOs
            target = max(tables, key=lambda t: len(t.find_all("tr")))
            rows = target.find_all("tr")
            for row in rows[1:]:  # skip header row
                cols = row.find_all("td")
                if len(cols) < 4:
                    continue
                try:
                    company = cols[0].get_text(strip=True)
                    if not company or company.lower() in ["ipo name", "ipo", "company", ""]:
                        continue

                    # col1 = issue price, col2 = GMP, col3 = listing price
                    issue_nums = re.findall(r"\d+\.?\d*", cols[1].get_text(strip=True).replace(",", ""))
                    gmp_nums   = re.findall(r"[-+]?\d+\.?\d*", cols[2].get_text(strip=True).replace(",", ""))
                    list_nums  = re.findall(r"\d+\.?\d*", cols[3].get_text(strip=True).replace(",", ""))

                    issue_price   = float(issue_nums[0]) if issue_nums else 0
                    gmp_val       = float(gmp_nums[0]) if gmp_nums else 0
                    listing_price = float(list_nums[0]) if list_nums else 0

                    # Only include if listing price is real (not zero, not same as issue)
                    if listing_price <= 0 or issue_price <= 0:
                        continue

                    listing_gain = round(((listing_price - issue_price) / issue_price) * 100, 2)

                    listed.append({
                        "company": company,
                        "symbol": "",
                        "listing_date": "",
                        "issue_price": issue_price,
                        "listing_price": listing_price,
                        "listing_gain": listing_gain,
                        "gmp_at_listing": gmp_val,
                        "status": "Listed",
                        "source": "ipowatch.in"
                    })
                except:
                    continue
        except Exception as e:
            print(f"fetch_listed error: {e}")
        return listed[:20]

    # ── SUBSCRIPTION DATA FROM IPOWATCH ──────────────────────────────────────
    def fetch_subscription_data(self, company_name, symbol=""):
        """Fetch subscription data from ipowatch.in"""
        try:
            slug = re.sub(r"[^a-z0-9]+", "-", company_name.lower()).strip("-")
            url = f"https://ipowatch.in/{slug}-ipo-subscription-status/"
            r = self._get(url, timeout=12)
            if r.status_code == 200 and "subscription" in r.text.lower():
                soup = BeautifulSoup(r.text, "html.parser")
                result = {"qib": 0, "hni": 0, "retail": 0, "employee": 0, "total": 0, "source": "ipowatch.in"}
                for row in soup.find_all("tr"):
                    text = row.get_text(strip=True).lower()
                    nums = re.findall(r"\d+\.?\d*", row.get_text())
                    if not nums:
                        continue
                    val = float(nums[0])
                    if "qib" in text:
                        result["qib"] = val
                    elif "nii" in text or "hni" in text or "non-institutional" in text:
                        result["hni"] = val
                    elif "retail" in text or "rii" in text:
                        result["retail"] = val
                    elif "employee" in text:
                        result["employee"] = val
                    elif "total" in text or "overall" in text:
                        result["total"] = val
                if result["total"] > 0 or result["qib"] > 0:
                    return result
        except Exception as e:
            print(f"Subscription error: {e}")
        return {"qib": 0, "hni": 0, "retail": 0, "employee": 0, "total": 0, "source": "unavailable"}

    # ── ALLOTMENT STATUS ─────────────────────────────────────────────────────
    def check_allotment_status(self, pan, company_name=""):
        registrars = {
            "KFintech (Karvy)": ("https://ipostatus.kfintech.com", "Hyundai, Swiggy, NTPC Green, Bajaj Housing"),
            "Link Intime India": ("https://linkintime.co.in/initial_offer/public-issues.html", "Waaree, Sagility, Afcons"),
            "Bigshare Services": ("https://www.bigshareonline.com/IPOAllotment.aspx", "SME IPOs"),
            "Cameo Corporate": ("https://cameoindiaonline.com/IPOAllotment.aspx", "Various IPOs"),
            "Skyline Financial": ("https://www.skylinerta.com/ipo.php", "Various IPOs"),
        }
        return {
            "pan": pan,
            "status": "Use registrar links below",
            "registrars": registrars,
            "note": "Allotment is typically 6 days after IPO close. Listing is 7 days after close."
        }

    # ── PREDICTION MODEL ─────────────────────────────────────────────────────
    def predict_listing_gain(self, ipo):
        """Real prediction using GMP + subscription data"""
        company = ipo.get("company", "")
        issue_price = ipo.get("issue_price", 0) or self._parse_price(ipo.get("price_band", "0"))
        gmp = ipo.get("gmp", 0)
        gmp_pct = ipo.get("gmp_percent", 0)
        sub = self.fetch_subscription_data(company)
        total_sub = sub.get("total", 0)
        qib_sub = sub.get("qib", 0)
        retail_sub = sub.get("retail", 0)
        hni_sub = sub.get("hni", 0)

        score = 0
        signals = []

        # GMP (45% weight)
        if gmp_pct > 40:
            score += 45; signals.append(f"Exceptional GMP: +{gmp_pct:.1f}% — est. listing ₹{ipo.get('est_listing_price', 0):.0f}")
        elif gmp_pct > 20:
            score += 35; signals.append(f"Strong GMP: +{gmp_pct:.1f}%")
        elif gmp_pct > 10:
            score += 25; signals.append(f"Moderate GMP: +{gmp_pct:.1f}%")
        elif gmp_pct > 0:
            score += 12; signals.append(f"Weak positive GMP: +{gmp_pct:.1f}%")
        elif gmp_pct < -5:
            score -= 25; signals.append(f"Negative GMP: {gmp_pct:.1f}% — listing loss likely")
        elif gmp_pct < 0:
            score -= 10; signals.append(f"Slightly negative GMP: {gmp_pct:.1f}%")
        else:
            signals.append("GMP data not yet available")

        # Subscription (35% weight)
        if total_sub > 100:
            score += 35; signals.append(f"Mega subscription: {total_sub:.0f}x oversubscribed")
        elif total_sub > 50:
            score += 28; signals.append(f"Exceptional subscription: {total_sub:.0f}x")
        elif total_sub > 20:
            score += 22; signals.append(f"Strong subscription: {total_sub:.0f}x")
        elif total_sub > 10:
            score += 15; signals.append(f"Good subscription: {total_sub:.0f}x")
        elif total_sub > 5:
            score += 8; signals.append(f"Moderate subscription: {total_sub:.0f}x")
        elif total_sub > 1:
            score += 3; signals.append(f"Low subscription: {total_sub:.1f}x")
        elif total_sub > 0:
            score -= 10; signals.append(f"Very low subscription: {total_sub:.1f}x — risky")

        # QIB (15% weight)
        if qib_sub > 50:
            score += 15; signals.append(f"Massive QIB interest: {qib_sub:.0f}x")
        elif qib_sub > 20:
            score += 10; signals.append(f"Strong QIB: {qib_sub:.0f}x")
        elif qib_sub > 5:
            score += 5; signals.append(f"Decent QIB: {qib_sub:.0f}x")

        # Retail (5% weight)
        if retail_sub > 10:
            score += 5; signals.append(f"High retail demand: {retail_sub:.0f}x")

        if score >= 70:
            rec, color, est_gain, conf = "STRONG APPLY", "#00ff88", max(gmp_pct, 30), 90
        elif score >= 50:
            rec, color, est_gain, conf = "APPLY", "#17a2b8", max(gmp_pct, 15), 78
        elif score >= 30:
            rec, color, est_gain, conf = "NEUTRAL", "#ffc107", max(gmp_pct, 5), 60
        elif score >= 10:
            rec, color, est_gain, conf = "AVOID", "#ff9800", gmp_pct, 65
        else:
            rec, color, est_gain, conf = "STRONG AVOID", "#ff5252", min(gmp_pct, -5), 72

        est_listing = round(issue_price * (1 + est_gain / 100), 2) if issue_price > 0 else ipo.get("est_listing_price", 0)
        stop_loss = round(issue_price * 0.92, 2) if issue_price > 0 else 0

        return {
            "recommendation": rec, "color": color, "score": score,
            "confidence": conf, "est_listing_gain": round(est_gain, 1),
            "est_listing_price": est_listing, "stop_loss": stop_loss,
            "gmp": gmp, "gmp_percent": gmp_pct,
            "sub_total": total_sub, "sub_qib": qib_sub,
            "sub_retail": retail_sub, "sub_hni": hni_sub,
            "signals": signals
        }

    # ── POST-LISTING ANALYSIS WITH REAL PRICES ───────────────────────────────
    def _resolve_nse_symbol(self, company_name):
        """Search NSE for the correct symbol of a company"""
        # Try NSE search API first
        try:
            query = company_name.split()[0]  # Use first word for search
            url = f"https://www.nseindia.com/api/search/autocomplete?q={query}"
            r = self.session.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                symbols = data.get("symbols", [])
                for item in symbols:
                    if item.get("symbol_info", "").upper() == "EQ":
                        return item.get("symbol", "")
                if symbols:
                    return symbols[0].get("symbol", "")
        except:
            pass

        # Try Yahoo Finance search
        try:
            query = company_name.replace(" ", "+") + "+NSE"
            url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&lang=en-US&region=IN&quotesCount=5"
            r = self.session.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                quotes = data.get("quotes", [])
                for q in quotes:
                    sym = q.get("symbol", "")
                    if sym.endswith(".NS") or sym.endswith(".BO"):
                        return sym.replace(".NS", "").replace(".BO", "")
        except:
            pass

        # Fallback: clean company name to symbol
        clean = re.sub(r"\b(limited|ltd|pvt|private|india|industries|technologies|tech|solutions|services|enterprises|group|holdings|finance|capital|energy|power|infra|infrastructure)\b",
                       "", company_name.lower())
        clean = re.sub(r"[^a-z0-9]", "", clean)
        return clean[:10].upper()

    def get_post_listing_analysis(self, listed_ipos):
        """Enrich listed IPOs with real-time Yahoo Finance data"""
        results = []
        for ipo in listed_ipos:
            company = ipo.get("company", "")
            issue_price = float(ipo.get("issue_price", 0) or 0)
            listing_price = float(ipo.get("listing_price", 0) or 0)
            if issue_price == 0:
                continue

            # Resolve symbol dynamically
            symbol = ipo.get("symbol", "") or self._resolve_nse_symbol(company)
            ns_symbol = f"{symbol}.NS" if not symbol.endswith(".NS") and not symbol.endswith(".BO") else symbol

            # Try .NS first, then .BO (BSE)
            ticker = None
            for suffix in [".NS", ".BO"]:
                sym_try = symbol + suffix if not symbol.endswith((".NS", ".BO")) else symbol
                try:
                    t = yf.Ticker(sym_try)
                    hist_test = t.history(period="1d")
                    if not hist_test.empty:
                        ticker = t
                        ns_symbol = sym_try
                        break
                except:
                    continue

            if ticker is None:
                print(f"Symbol not found for: {company} (tried {symbol})")
                continue

            try:
                hist_1d = ticker.history(period="1d")
                hist_1mo = ticker.history(period="1mo")
                hist_3mo = ticker.history(period="3mo")
                if hist_1d.empty:
                    continue
                current_price = float(hist_1d["Close"].iloc[-1])
                day_high = float(hist_1d["High"].iloc[-1])
                day_low = float(hist_1d["Low"].iloc[-1])
                volume = float(hist_1d["Volume"].iloc[-1])
                avg_vol = float(hist_1mo["Volume"].mean()) if not hist_1mo.empty else volume
                total_return = round(((current_price - issue_price) / issue_price) * 100, 2)
                listing_gain_calc = round(((listing_price - issue_price) / issue_price) * 100, 2) if listing_price > 0 else 0
                support = float(hist_3mo["Low"].min()) if not hist_3mo.empty else current_price * 0.90
                resistance = float(hist_3mo["High"].max()) if not hist_3mo.empty else current_price * 1.15
                rsi = 50.0
                if not hist_1mo.empty and len(hist_1mo) >= 14:
                    delta = hist_1mo["Close"].diff()
                    gain_s = delta.where(delta > 0, 0).rolling(14).mean()
                    loss_s = (-delta.where(delta < 0, 0)).rolling(14).mean()
                    rs = gain_s / loss_s
                    rsi_s = 100 - (100 / (1 + rs))
                    rsi = float(rsi_s.iloc[-1])
                volatility = 0.0
                if not hist_1mo.empty and len(hist_1mo) > 1:
                    volatility = float(hist_1mo["Close"].pct_change().std() * (252 ** 0.5) * 100)
                target_1 = round(issue_price * 1.20, 2)
                target_2 = round(issue_price * 1.40, 2)
                stop_loss = round(max(issue_price * 0.90, current_price * 0.88), 2)
                if current_price >= target_2:
                    alert, ac, am = "BOOK ALL PROFITS", "#00ff88", f"Target 2 hit! {total_return:+.1f}% gain. Exit full position."
                elif current_price >= target_1:
                    alert, ac, am = "BOOK 50% PROFITS", "#17a2b8", f"Target 1 hit! Book 50% at Rs{current_price:.2f}, trail SL for rest."
                elif current_price <= stop_loss:
                    alert, ac, am = "STOP LOSS HIT", "#ff5252", f"SL breached at Rs{current_price:.2f}. Exit to limit losses."
                elif total_return > 15:
                    alert, ac, am = "HOLD - TRAIL SL", "#ffc107", f"Good gains {total_return:+.1f}%. Trail SL to Rs{current_price*0.92:.2f}."
                elif total_return < -10:
                    alert, ac, am = "REVIEW POSITION", "#ff9800", f"Down {total_return:.1f}%. Review before averaging."
                else:
                    alert, ac, am = "HOLD", "#e0e0e0", f"Holding at {total_return:+.1f}%. Targets: Rs{target_1:.0f} / Rs{target_2:.0f}."
                info = ticker.info
                results.append({
                    "company": company, "symbol": ns_symbol,
                    "sector": info.get("sector", "N/A"),
                    "issue_price": issue_price, "listing_price": listing_price,
                    "current_price": current_price, "day_high": day_high, "day_low": day_low,
                    "volume": volume, "avg_volume": avg_vol,
                    "volume_ratio": round(volume / avg_vol, 2) if avg_vol > 0 else 1,
                    "listing_gain": listing_gain_calc, "total_return": total_return,
                    "rsi": round(rsi, 1), "volatility": round(volatility, 1),
                    "support": round(support, 2), "resistance": round(resistance, 2),
                    "target_1": target_1, "target_2": target_2, "stop_loss": stop_loss,
                    "alert": alert, "alert_color": ac, "alert_msg": am,
                    "market_cap": info.get("marketCap", 0),
                    "pe_ratio": info.get("trailingPE", 0),
                    "week_52_high": info.get("fiftyTwoWeekHigh", 0),
                    "week_52_low": info.get("fiftyTwoWeekLow", 0),
                    "listing_date": ipo.get("listing_date", "")
                })
            except Exception as e:
                print(f"Error enriching {company}: {e}")
                continue
        return results

    # ── NEWS SENTIMENT ───────────────────────────────────────────────────────
    def fetch_ipo_news(self, company_name):
        news_items = []
        avg_sentiment = 0.0
        try:
            query = company_name.replace(" ", "+") + "+IPO+India"
            url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
            r = self._get(url, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "xml")
                items = soup.find_all("item")[:8]
                sentiments = []
                for item in items:
                    title = item.title.text if item.title else ""
                    source = item.source.text if item.source else "Google News"
                    pub_date = item.pubDate.text if item.pubDate else ""
                    try:
                        s = TextBlob(title).sentiment.polarity
                    except:
                        s = 0.0
                    sentiments.append(s)
                    news_items.append({
                        "title": title, "source": source, "date": pub_date,
                        "sentiment": s,
                        "label": "Positive" if s > 0.1 else "Negative" if s < -0.1 else "Neutral"
                    })
                avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
        except Exception as e:
            print(f"News error: {e}")
        label = "Positive" if avg_sentiment > 0.1 else "Negative" if avg_sentiment < -0.1 else "Neutral"
        return {"news": news_items, "avg_sentiment": round(avg_sentiment, 3), "label": label}
