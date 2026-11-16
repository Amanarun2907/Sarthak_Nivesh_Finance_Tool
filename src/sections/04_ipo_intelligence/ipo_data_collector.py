# Sarthak Nivesh - IPO Data Collector
# Real-time IPO data collection from Indian markets
# Team: Aman Jain, Rohit Fogla, Vanshita Mehta, Disita Tirthani

import re
import time
import sqlite3
from datetime import datetime, timedelta
from urllib.parse import quote

import feedparser
import pandas as pd
import requests
import yfinance as yf

from config import *


class IPODataCollector:
    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121.0.0.0 Safari/537.36"
            )
        }
        print("✅ IPO Data Collector initialized")

    def _get_nse_json(self, url):
        """Fetch JSON data from NSE India with session headers/cookies."""
        try:
            session = requests.Session()
            session.headers.update(self.headers)
            session.get("https://www.nseindia.com", timeout=10)
            response = session.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"❌ NSE fetch error: {str(e)}")
        return None

    def _parse_issue_price(self, value):
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        text = str(value).replace("₹", "").replace(",", "").strip()
        if "-" in text:
            parts = [p.strip() for p in text.split("-") if p.strip()]
            try:
                return float(parts[-1])
            except Exception:
                return None
        try:
            return float(text)
        except Exception:
            return None

    def _parse_issue_size(self, value):
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        text = str(value).replace(",", "").lower()
        numbers = re.findall(r"[\d.]+", text)
        if not numbers:
            return None
        size = float(numbers[0])
        if "crore" in text:
            return size
        if "lac" in text or "lakh" in text:
            return size / 100.0
        return size

    def scrape_nse_ipo_data(self):
        """Fetch IPO data from NSE India APIs (real data)."""
        try:
            print("🔍 Collecting IPO data from NSE India...")
            ipos = []

            current_url = "https://www.nseindia.com/api/ipo-current-issue"
            current_data = self._get_nse_json(current_url)
            if isinstance(current_data, dict) and "data" in current_data:
                ipos.extend(current_data["data"])

            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=365)
            past_url = (
                "https://www.nseindia.com/api/ipo-past-issue"
                f"?from={start_date.strftime('%d-%m-%Y')}"
                f"&to={end_date.strftime('%d-%m-%Y')}"
            )
            past_data = self._get_nse_json(past_url)
            if isinstance(past_data, dict) and "data" in past_data:
                ipos.extend(past_data["data"])

            cleaned = []
            for item in ipos:
                company_name = item.get("companyName") or item.get("company") or item.get("name")
                symbol = item.get("symbol") or item.get("symbolName") or item.get("ticker")
                listing_date = item.get("listingDate") or item.get("listingdate")
                issue_price = self._parse_issue_price(
                    item.get("issuePrice") or item.get("priceBand") or item.get("issuePriceBand")
                )
                issue_size = self._parse_issue_size(
                    item.get("issueSize") or item.get("issueSizeInCr") or item.get("issueSizeCr")
                )
                subscription_times = item.get("subscription") or item.get("subscriptionTimes")
                sector = item.get("industry") or item.get("sector") or "Unknown"

                if not company_name or not listing_date:
                    continue

                try:
                    listing_date = datetime.strptime(listing_date[:10], "%d-%m-%Y").strftime(
                        "%Y-%m-%d"
                    )
                except Exception:
                    try:
                        listing_date = datetime.strptime(listing_date[:10], "%Y-%m-%d").strftime(
                            "%Y-%m-%d"
                        )
                    except Exception:
                        listing_date = None

                if not listing_date:
                    continue

                cleaned.append(
                    {
                        "company_name": company_name,
                        "symbol": symbol or "",
                        "listing_date": listing_date,
                        "issue_price": issue_price,
                        "issue_size_crores": issue_size,
                        "subscription_times": float(subscription_times)
                        if subscription_times not in (None, "")
                        else None,
                        "sector": sector,
                        "market_cap_category": "Unknown",
                    }
                )
            # If NSE API returns nothing (rate limiting / website change),
            # fall back to a small, hard-coded list of REAL recent Indian IPOs.
            if not cleaned:
                print("⚠️ NSE API returned no IPO records. Using fallback list of real recent IPOs.")
                cleaned = [
                    {
                        "company_name": "Tata Technologies Limited",
                        "symbol": "TATATECH.NS",
                        "listing_date": "2023-11-30",
                        "issue_price": 500.0,
                        "issue_size_crores": 3042.51,
                        "subscription_times": 69.43,
                        "sector": "Technology",
                        "market_cap_category": "Large Cap",
                    },
                    {
                        "company_name": "Indian Renewable Energy Development Agency Ltd",
                        "symbol": "IREDA.NS",
                        "listing_date": "2023-11-29",
                        "issue_price": 32.0,
                        "issue_size_crores": 2150.21,
                        "subscription_times": 38.27,
                        "sector": "Financial Services",
                        "market_cap_category": "Mid Cap",
                    },
                    {
                        "company_name": "Kaynes Technology India Ltd",
                        "symbol": "KAYNES.NS",
                        "listing_date": "2022-11-22",
                        "issue_price": 587.0,
                        "issue_size_crores": 858.00,
                        "subscription_times": 34.16,
                        "sector": "Technology",
                        "market_cap_category": "Mid Cap",
                    },
                    {
                        "company_name": "EMS Ltd",
                        "symbol": "EMS.NS",
                        "listing_date": "2023-09-21",
                        "issue_price": 211.0,
                        "issue_size_crores": 321.00,
                        "subscription_times": 76.21,
                        "sector": "Infrastructure",
                        "market_cap_category": "Small Cap",
                    },
                ]

            print(f"✅ Collected {len(cleaned)} IPO records (NSE + real fallback list)")
            return cleaned

        except Exception as e:
            print(f"❌ Error scraping IPO data: {str(e)}")
            return []

    def get_ipo_price_data(self, symbol, listing_date):
        """Get real price data for IPO using Yahoo Finance."""
        try:
            if not symbol:
                return None
            print(f"📈 Getting price data for {symbol}...")

            ticker = yf.Ticker(symbol)
            listing_dt = datetime.strptime(listing_date, "%Y-%m-%d")
            start_date = listing_dt - timedelta(days=5)
            end_date = datetime.now()

            hist_data = ticker.history(start=start_date, end=end_date)
            if hist_data.empty:
                print(f"⚠️ No price data available for {symbol}")
                return None

            price_data = {}
            listing_day_data = hist_data[hist_data.index.date >= listing_dt.date()]

            if not listing_day_data.empty:
                listing_day = listing_day_data.index[0]
                price_data["listing_price"] = float(listing_day_data.loc[listing_day, "Close"])
                price_data["listing_volume"] = int(listing_day_data.loc[listing_day, "Volume"])

                days_after_listing = []
                for i, (date, row) in enumerate(listing_day_data.iterrows()):
                    days_after_listing.append(
                        {
                            "day": i,
                            "date": date.strftime("%Y-%m-%d"),
                            "price": float(row["Close"]),
                            "volume": int(row["Volume"]),
                            "high": float(row["High"]),
                            "low": float(row["Low"]),
                        }
                    )

                price_data["daily_data"] = days_after_listing

                if len(days_after_listing) > 0:
                    current_price = days_after_listing[-1]["price"]
                    price_data["current_price"] = current_price

                    for period in [1, 7, 30, 60, 90]:
                        if len(days_after_listing) > period:
                            period_price = days_after_listing[min(period, len(days_after_listing) - 1)][
                                "price"
                            ]
                            price_data[f"price_day_{period}"] = period_price

            return price_data

        except Exception as e:
            print(f"❌ Error getting price data for {symbol}: {str(e)}")
            return None

    def collect_ipo_news(self, company_name):
        """Collect real news articles related to IPO."""
        try:
            print(f"📰 Collecting news for {company_name} IPO...")

            news_articles = []

            rss_url = (
                "https://news.google.com/rss/search?q="
                + quote(f"{company_name} IPO India")
                + "&hl=en-IN&gl=IN&ceid=IN:en"
            )
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:20]:
                news_articles.append(
                    {
                        "title": entry.title,
                        "content": entry.get("summary", ""),
                        "source": entry.get("source", {}).get("title", "Google News"),
                        "published_date": datetime(*entry.published_parsed[:6])
                        if hasattr(entry, "published_parsed")
                        else datetime.now(),
                    }
                )

            if NEWS_API_KEY:
                try:
                    params = {
                        "q": f"{company_name} IPO",
                        "language": "en",
                        "sortBy": "publishedAt",
                        "pageSize": 20,
                        "apiKey": NEWS_API_KEY,
                    }
                    response = requests.get(
                        "https://newsapi.org/v2/everything", params=params, timeout=10
                    )
                    if response.status_code == 200:
                        data = response.json()
                        for article in data.get("articles", []):
                            news_articles.append(
                                {
                                    "title": article.get("title"),
                                    "content": article.get("description") or "",
                                    "source": (article.get("source") or {}).get("name", "NewsAPI"),
                                    "published_date": article.get("publishedAt", datetime.now()),
                                }
                            )
                except Exception as e:
                    print(f"❌ NewsAPI error: {str(e)}")

            return news_articles

        except Exception as e:
            print(f"❌ Error collecting news: {str(e)}")
            return []

    def get_sector_performance(self, sector):
        """Get sector performance data for context."""
        try:
            sector_indices = {
                "Technology": "^CNXIT",
                "Financial Services": "^NSEBANK",
                "Real Estate Investment Trust": "^NSEI",
                "Oil & Gas": "^CNXENERGY",
                "Travel & Tourism": "^NSEI",
            }

            index_symbol = sector_indices.get(sector, "^NSEI")
            ticker = yf.Ticker(index_symbol)
            hist_data = ticker.history(period="3mo")

            if not hist_data.empty:
                current_price = hist_data["Close"].iloc[-1]
                start_price = hist_data["Close"].iloc[0]
                sector_performance = ((current_price - start_price) / start_price) * 100

                return {
                    "sector_performance_3m": round(sector_performance, 2),
                    "sector_volatility": round(hist_data["Close"].pct_change().std() * 100, 2),
                }

            return {"sector_performance_3m": 0.0, "sector_volatility": 20.0}

        except Exception as e:
            print(f"❌ Error getting sector performance: {str(e)}")
            return {"sector_performance_3m": 0.0, "sector_volatility": 20.0}

    def comprehensive_ipo_data_collection(self):
        """Collect comprehensive IPO data from all sources."""
        try:
            print("🚀 Starting comprehensive IPO data collection...")

            ipo_list = self.scrape_nse_ipo_data()
            comprehensive_data = []

            for ipo in ipo_list:
                print(f"\n📊 Processing {ipo['company_name']}...")

                price_data = None
                if ipo.get("symbol") and ipo.get("listing_date"):
                    price_data = self.get_ipo_price_data(ipo["symbol"], ipo["listing_date"])

                news_data = self.collect_ipo_news(ipo["company_name"])
                sector_data = self.get_sector_performance(ipo.get("sector", "Unknown"))

                comprehensive_ipo = {
                    **ipo,
                    "price_data": price_data,
                    "news_data": news_data,
                    "sector_data": sector_data,
                    "collection_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }

                comprehensive_data.append(comprehensive_ipo)
                time.sleep(1)

            print(f"✅ IPO data collection completed for {len(comprehensive_data)} IPOs")
            return comprehensive_data

        except Exception as e:
            print(f"❌ Error in comprehensive data collection: {str(e)}")
            return []

    def update_ipo_database(self, ipo_data_list):
        """Update IPO database with collected data."""
        try:
            print("💾 Updating IPO database with collected data...")

            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()

            for ipo_data in ipo_data_list:
                cursor.execute("SELECT id FROM ipo_intelligence WHERE symbol = ?", (ipo_data["symbol"],))
                existing = cursor.fetchone()

                if existing:
                    update_query = """
                        UPDATE ipo_intelligence SET
                        company_name = ?, listing_date = ?, issue_price = ?,
                        issue_size_crores = ?, subscription_times = ?, sector = ?,
                        market_cap_category = ?, last_updated = CURRENT_TIMESTAMP
                        WHERE symbol = ?
                    """
                    cursor.execute(
                        update_query,
                        (
                            ipo_data["company_name"],
                            ipo_data["listing_date"],
                            ipo_data["issue_price"],
                            ipo_data["issue_size_crores"],
                            ipo_data["subscription_times"],
                            ipo_data["sector"],
                            ipo_data["market_cap_category"],
                            ipo_data["symbol"],
                        ),
                    )
                else:
                    insert_query = """
                        INSERT INTO ipo_intelligence
                        (company_name, symbol, listing_date, issue_price, issue_size_crores,
                         subscription_times, sector, market_cap_category)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    cursor.execute(
                        insert_query,
                        (
                            ipo_data["company_name"],
                            ipo_data["symbol"],
                            ipo_data["listing_date"],
                            ipo_data["issue_price"],
                            ipo_data["issue_size_crores"],
                            ipo_data["subscription_times"],
                            ipo_data["sector"],
                            ipo_data["market_cap_category"],
                        ),
                    )

                if ipo_data.get("price_data"):
                    price_data = ipo_data["price_data"]
                    update_fields = []
                    update_values = []

                    if "listing_price" in price_data:
                        update_fields.append("listing_price = ?")
                        update_values.append(price_data["listing_price"])

                    if "current_price" in price_data:
                        update_fields.append("price_day_90 = ?")
                        update_values.append(price_data["current_price"])

                    if update_fields:
                        update_values.append(ipo_data["symbol"])
                        price_update_query = (
                            f"UPDATE ipo_intelligence SET {', '.join(update_fields)} WHERE symbol = ?"
                        )
                        cursor.execute(price_update_query, update_values)

            conn.commit()
            conn.close()

            print(f"✅ Database updated with {len(ipo_data_list)} IPO records")

        except Exception as e:
            print(f"❌ Error updating database: {str(e)}")


if __name__ == "__main__":
    print("🔍 Testing IPO Data Collector...")
    collector = IPODataCollector()
    comprehensive_data = collector.comprehensive_ipo_data_collection()
    if comprehensive_data:
        collector.update_ipo_database(comprehensive_data)
    print("✅ IPO Data Collector test completed!")
