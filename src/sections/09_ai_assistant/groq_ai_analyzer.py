# Groq AI Analyzer - Indian Stock Market Expert
import requests


class GroqAIAnalyzer:

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key,
        }
        self._system = (
            "You are an expert Indian stock market investment advisor with deep knowledge of "
            "NSE, BSE, Nifty 50, Sensex, mutual funds, IPOs, and Indian economy. "
            "Provide accurate, concise, actionable advice. Always mention risks. "
            "Focus on Indian markets and instruments. Keep responses under 350 words."
        )

    def _call_groq(self, user_prompt, system_override=None):
        """Call Groq API with proper system + user message separation."""
        try:
            payload = {
                "model": "openai/gpt-oss-120b",
                "temperature": 0.7,
                "max_tokens": 600,
                "messages": [
                    {
                        "role": "system",
                        "content": system_override if system_override else self._system,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
            }
            r = requests.post(
                self.base_url, headers=self.headers, json=payload, timeout=30
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            else:
                print("Groq API error " + str(r.status_code) + ": " + r.text[:200])
                return None
        except Exception as e:
            print("Groq call error: " + str(e))
            return None

    def analyze_market_sentiment(self, news_items):
        try:
            news_summary = "\n".join([
                "- " + n["title"] + " (Sentiment: " + n.get("sentiment_analysis", {}).get("sentiment", "N/A") + ")"
                for n in news_items[:10]
            ])
            prompt = (
                "Analyze these recent Indian market news headlines:\n\n"
                + news_summary
                + "\n\nProvide:\n"
                "1. Overall sentiment (Bullish/Bearish/Neutral)\n"
                "2. Key market drivers (3 points)\n"
                "3. Sectors to watch\n"
                "4. Short-term outlook\n\n"
                "Keep under 150 words."
            )
            return self._call_groq(prompt)
        except Exception as e:
            print("Sentiment analysis error: " + str(e))
            return None

    def get_news_summary(self, news_items):
        try:
            news_text = "\n".join([
                str(i + 1) + ". " + n["title"]
                for i, n in enumerate(news_items[:8])
            ])
            prompt = "Summarize these Indian market news in 3-4 key bullet points:\n\n" + news_text
            return self._call_groq(prompt)
        except Exception as e:
            print("News summary error: " + str(e))
            return None
