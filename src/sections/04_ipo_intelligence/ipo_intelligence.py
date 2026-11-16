# Sarthak Nivesh - IPO Intelligence System (Unique Feature)
# Post-IPO Liquidity & Retail Sentiment Forecast
# Team: Aman Jain, Rohit Fogla, Vanshita Mehta, Disita Tirthani

import sqlite3
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from config import *
from ipo_data_collector import IPODataCollector


class IPOIntelligenceSystem:
    def __init__(self):
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.collector = IPODataCollector()
        self.setup_ipo_database()
        print("✅ IPO Intelligence System initialized")

    def setup_ipo_database(self):
        """Setup IPO-specific database tables."""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ipo_intelligence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    listing_date DATE NOT NULL,
                    issue_price REAL NOT NULL,
                    issue_size_crores REAL,
                    subscription_times REAL,
                    listing_price REAL,
                    listing_gains_percent REAL,

                    price_day_1 REAL,
                    price_day_7 REAL,
                    price_day_30 REAL,
                    price_day_60 REAL,
                    price_day_90 REAL,

                    performance_1d REAL,
                    performance_7d REAL,
                    performance_30d REAL,
                    performance_60d REAL,
                    performance_90d REAL,

                    volume_day_1 INTEGER,
                    volume_day_7_avg INTEGER,
                    volume_day_30_avg INTEGER,
                    liquidity_score REAL,

                    news_sentiment_score REAL,
                    social_sentiment_score REAL,
                    retail_sentiment_score REAL,
                    overall_sentiment_score REAL,

                    recommendation TEXT,
                    confidence_score REAL,
                    hold_exit_advice TEXT,
                    target_price REAL,
                    stop_loss REAL,

                    volatility_score REAL,
                    risk_rating TEXT,
                    liquidity_risk TEXT,

                    sector TEXT,
                    market_cap_category TEXT,
                    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ipo_news_sentiment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ipo_symbol TEXT NOT NULL,
                    news_title TEXT,
                    news_content TEXT,
                    news_source TEXT,
                    sentiment_score REAL,
                    published_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            conn.commit()
            conn.close()
            print("✅ IPO Intelligence database setup complete")

        except Exception as e:
            print(f"❌ Error setting up IPO database: {str(e)}")

    def collect_recent_ipos(self):
        """Collect recent IPO data from NSE India (real data only)."""
        try:
            recent_ipos = self.collector.scrape_nse_ipo_data()
            if not recent_ipos:
                return []

            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()

            for ipo in recent_ipos:
                cursor.execute("SELECT id FROM ipo_intelligence WHERE symbol = ?", (ipo["symbol"],))
                if cursor.fetchone() is None:
                    cursor.execute(
                        """
                        INSERT INTO ipo_intelligence
                        (company_name, symbol, listing_date, issue_price, issue_size_crores,
                         subscription_times, sector, market_cap_category)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            ipo["company_name"],
                            ipo["symbol"],
                            ipo["listing_date"],
                            ipo["issue_price"],
                            ipo["issue_size_crores"],
                            ipo["subscription_times"],
                            ipo["sector"],
                            ipo["market_cap_category"],
                        ),
                    )

            conn.commit()
            conn.close()

            print(f"✅ Collected {len(recent_ipos)} recent IPOs")
            return recent_ipos

        except Exception as e:
            print(f"❌ Error collecting IPO data: {str(e)}")
            return []

    def _get_price_at_offset(self, data, start_idx, offset):
        idx = start_idx + offset
        if idx < len(data):
            return float(data.iloc[idx]["Close"])
        return None

    def analyze_post_ipo_performance(self, symbol):
        """Analyze post-IPO performance using real market data."""
        try:
            print(f"📊 Analyzing post-IPO performance for {symbol}...")

            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ipo_intelligence WHERE symbol = ?", (symbol,))
            ipo_data = cursor.fetchone()
            if not ipo_data:
                print(f"❌ No IPO data found for {symbol}")
                return None

            columns = [description[0] for description in cursor.description]
            ipo_dict = dict(zip(columns, ipo_data))
            conn.close()

            listing_date = datetime.strptime(ipo_dict["listing_date"], "%Y-%m-%d")
            issue_price = ipo_dict["issue_price"]

            ticker = yf.Ticker(symbol)
            start_date = listing_date - timedelta(days=5)
            end_date = datetime.now()
            hist_data = ticker.history(start=start_date, end=end_date)

            if hist_data.empty:
                print(f"⚠️ No price data available for {symbol}")
                return None

            listing_idx = None
            for idx, dt in enumerate(hist_data.index):
                if dt.date() >= listing_date.date():
                    listing_idx = idx
                    break

            if listing_idx is None:
                print(f"⚠️ No trading data on/after listing date for {symbol}")
                return None

            price_day_1 = self._get_price_at_offset(hist_data, listing_idx, 0)
            price_day_7 = self._get_price_at_offset(hist_data, listing_idx, 7)
            price_day_30 = self._get_price_at_offset(hist_data, listing_idx, 30)
            price_day_60 = self._get_price_at_offset(hist_data, listing_idx, 60)
            price_day_90 = self._get_price_at_offset(hist_data, listing_idx, 90)

            def perf(price):
                return ((price - issue_price) / issue_price) * 100 if price else None

            volume_day_1 = int(hist_data.iloc[listing_idx]["Volume"])
            volume_day_7_avg = (
                int(hist_data.iloc[listing_idx : listing_idx + 7]["Volume"].mean())
                if listing_idx + 7 <= len(hist_data)
                else int(hist_data.iloc[listing_idx:]["Volume"].mean())
            )
            volume_day_30_avg = (
                int(hist_data.iloc[listing_idx : listing_idx + 30]["Volume"].mean())
                if listing_idx + 30 <= len(hist_data)
                else int(hist_data.iloc[listing_idx:]["Volume"].mean())
            )

            liquidity_score = min(100, (volume_day_30_avg / 100000) * 10)
            returns = hist_data["Close"].pct_change().dropna()
            volatility_score = returns.std() * 100 if not returns.empty else 0.0

            performance_analysis = {
                "symbol": symbol,
                "listing_price": price_day_1,
                "listing_gains_percent": perf(price_day_1),
                "price_day_1": price_day_1,
                "price_day_7": price_day_7,
                "price_day_30": price_day_30,
                "price_day_60": price_day_60,
                "price_day_90": price_day_90,
                "performance_1d": perf(price_day_1),
                "performance_7d": perf(price_day_7),
                "performance_30d": perf(price_day_30),
                "performance_60d": perf(price_day_60),
                "performance_90d": perf(price_day_90),
                "volume_day_1": volume_day_1,
                "volume_day_7_avg": volume_day_7_avg,
                "volume_day_30_avg": volume_day_30_avg,
                "liquidity_score": round(liquidity_score, 2),
                "volatility_score": round(volatility_score, 2),
            }

            self.update_ipo_analysis(symbol, performance_analysis)
            return performance_analysis

        except Exception as e:
            print(f"❌ Error analyzing IPO performance: {str(e)}")
            return None

    def analyze_ipo_sentiment(self, symbol, company_name):
        """Analyze sentiment around IPO from real news sources."""
        try:
            print(f"📰 Analyzing sentiment for {company_name} IPO...")

            news_articles = self.collector.collect_ipo_news(company_name)
            if not news_articles:
                return None

            sentiment_scores = []
            for article in news_articles:
                text = f"{article.get('title', '')} {article.get('content', '')}"
                sentiment = self.sentiment_analyzer.polarity_scores(text)
                sentiment_scores.append(sentiment["compound"])

            news_sentiment = float(np.mean(sentiment_scores)) if sentiment_scores else 0.0
            social_sentiment = None
            retail_sentiment = news_sentiment
            overall_sentiment = news_sentiment

            sentiment_analysis = {
                "news_sentiment_score": round(news_sentiment, 3),
                "social_sentiment_score": social_sentiment,
                "retail_sentiment_score": round(retail_sentiment, 3),
                "overall_sentiment_score": round(overall_sentiment, 3),
            }

            self.update_ipo_analysis(symbol, sentiment_analysis)
            return sentiment_analysis

        except Exception as e:
            print(f"❌ Error analyzing IPO sentiment: {str(e)}")
            return None

    def generate_ipo_recommendation(self, symbol):
        """Generate hold/exit recommendation for IPO."""
        try:
            print(f"🎯 Generating IPO recommendation for {symbol}...")

            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ipo_intelligence WHERE symbol = ?", (symbol,))
            ipo_data = cursor.fetchone()
            if not ipo_data:
                return None

            columns = [description[0] for description in cursor.description]
            ipo_dict = dict(zip(columns, ipo_data))
            conn.close()

            performance_30d = ipo_dict.get("performance_30d") or 0
            performance_90d = ipo_dict.get("performance_90d") or 0
            overall_sentiment = ipo_dict.get("overall_sentiment_score") or 0
            volatility_score = ipo_dict.get("volatility_score") or 20
            liquidity_score = ipo_dict.get("liquidity_score") or 50

            recommendation_score = 0

            if performance_30d > 20:
                recommendation_score += 40
            elif performance_30d > 0:
                recommendation_score += 25
            elif performance_30d > -15:
                recommendation_score += 10

            if overall_sentiment > 0.3:
                recommendation_score += 30
            elif overall_sentiment > 0:
                recommendation_score += 20
            elif overall_sentiment > -0.2:
                recommendation_score += 10

            if liquidity_score > 70:
                recommendation_score += 20
            elif liquidity_score > 50:
                recommendation_score += 15
            elif liquidity_score > 30:
                recommendation_score += 10
            else:
                recommendation_score += 5

            if volatility_score < 15:
                recommendation_score += 10
            elif volatility_score < 25:
                recommendation_score += 7
            elif volatility_score < 35:
                recommendation_score += 5
            else:
                recommendation_score += 2

            if recommendation_score >= 80:
                recommendation = "STRONG HOLD"
                hold_exit_advice = "Strong fundamentals and positive sentiment. Hold for long-term gains."
                confidence_score = 85 + (recommendation_score - 80)
            elif recommendation_score >= 60:
                recommendation = "HOLD"
                hold_exit_advice = "Moderate performance with decent prospects. Hold with caution."
                confidence_score = 70 + (recommendation_score - 60)
            elif recommendation_score >= 40:
                recommendation = "PARTIAL EXIT"
                hold_exit_advice = "Mixed signals. Consider booking partial profits and hold remaining."
                confidence_score = 55 + (recommendation_score - 40)
            else:
                recommendation = "EXIT"
                hold_exit_advice = "Weak performance and sentiment. Consider exiting position."
                confidence_score = 40 + recommendation_score

            current_price = (
                ipo_dict.get("price_day_90")
                or ipo_dict.get("price_day_30")
                or ipo_dict.get("issue_price")
            )

            if recommendation in ["STRONG HOLD", "HOLD"]:
                target_price = current_price * 1.25
                stop_loss = current_price * 0.85
            else:
                target_price = current_price * 1.10
                stop_loss = current_price * 0.90

            if volatility_score > 30:
                risk_rating = "High Risk"
            elif volatility_score > 20:
                risk_rating = "Moderate Risk"
            else:
                risk_rating = "Low Risk"

            if liquidity_score > 70:
                liquidity_risk = "Low"
            elif liquidity_score > 40:
                liquidity_risk = "Moderate"
            else:
                liquidity_risk = "High"

            recommendation_data = {
                "recommendation": recommendation,
                "confidence_score": round(min(confidence_score, 95), 1),
                "hold_exit_advice": hold_exit_advice,
                "target_price": round(target_price, 2),
                "stop_loss": round(stop_loss, 2),
                "risk_rating": risk_rating,
                "liquidity_risk": liquidity_risk,
            }

            self.update_ipo_analysis(symbol, recommendation_data)
            return recommendation_data

        except Exception as e:
            print(f"❌ Error generating IPO recommendation: {str(e)}")
            return None

    def update_ipo_analysis(self, symbol, analysis_data):
        """Update IPO analysis in database."""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()

            update_fields = []
            update_values = []
            for key, value in analysis_data.items():
                if key != "symbol":
                    update_fields.append(f"{key} = ?")
                    update_values.append(value)

            update_values.append(symbol)
            query = (
                f"UPDATE ipo_intelligence SET {', '.join(update_fields)}, "
                "last_updated = CURRENT_TIMESTAMP WHERE symbol = ?"
            )

            cursor.execute(query, update_values)
            conn.commit()
            conn.close()
            print(f"✅ Updated IPO analysis for {symbol}")

        except Exception as e:
            print(f"❌ Error updating IPO analysis: {str(e)}")

    def comprehensive_ipo_analysis(self, symbol):
        """Perform comprehensive IPO analysis."""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ipo_intelligence WHERE symbol = ?", (symbol,))
            ipo_data = cursor.fetchone()
            if not ipo_data:
                print(f"❌ No IPO data found for {symbol}")
                return None

            columns = [description[0] for description in cursor.description]
            ipo_dict = dict(zip(columns, ipo_data))
            conn.close()

            performance_analysis = self.analyze_post_ipo_performance(symbol)
            sentiment_analysis = self.analyze_ipo_sentiment(symbol, ipo_dict["company_name"])
            recommendation_data = self.generate_ipo_recommendation(symbol)

            return {
                "basic_info": ipo_dict,
                "performance_analysis": performance_analysis,
                "sentiment_analysis": sentiment_analysis,
                "recommendation": recommendation_data,
                "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

        except Exception as e:
            print(f"❌ Error in comprehensive IPO analysis: {str(e)}")
            return None

    def get_all_ipo_analysis(self):
        """Get analysis for all IPOs in database."""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            df = pd.read_sql_query(
                "SELECT * FROM ipo_intelligence ORDER BY listing_date DESC", conn
            )
            conn.close()
            return df
        except Exception as e:
            print(f"❌ Error getting IPO analysis: {str(e)}")
            return pd.DataFrame()


if __name__ == "__main__":
    print("🚀 Testing IPO Intelligence System...")
    ipo_system = IPOIntelligenceSystem()
    recent_ipos = ipo_system.collect_recent_ipos()
    if recent_ipos:
        test_symbol = recent_ipos[0]["symbol"]
        ipo_system.comprehensive_ipo_analysis(test_symbol)
    print("✅ IPO Intelligence System test completed!")
