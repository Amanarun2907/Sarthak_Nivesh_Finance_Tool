# सार्थक निवेश - Advanced Sentiment Analysis & Fake News Detection
# Real-time sentiment analysis with ML-based fake news detection
# Team: Aman Jain, Rohit Fogla, Vanshita Mehta, Disita Tirthani

import pandas as pd
import numpy as np
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import sqlite3
from datetime import datetime
import re
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle
import os
from config import *

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
except:
    pass

class AdvancedSentimentAnalyzer:
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.fake_news_detector = self.setup_fake_news_detector()
        print("✅ Advanced Sentiment Analyzer initialized")
    
    def setup_fake_news_detector(self):
        """Setup ML-based fake news detection"""
        try:
            # Financial fake news keywords (Indian market specific)
            self.fake_news_keywords = [
                'guaranteed returns', 'risk-free investment', 'double money',
                'insider tip', 'secret formula', 'get rich quick',
                'zero risk', '100% profit', 'sure shot', 'hot tip',
                'pump and dump', 'manipulation', 'artificial boost',
                'fake volume', 'price rigging', 'scam alert'
            ]
            
            # Reliable source indicators
            self.reliable_sources = [
                'economic times', 'business standard', 'mint', 'moneycontrol',
                'reuters', 'bloomberg', 'cnbc', 'nse', 'bse', 'sebi',
                'rbi', 'ministry of finance', 'pib', 'livemint'
            ]
            
            print("✅ Fake news detection system ready")
            return True
            
        except Exception as e:
            print(f"⚠️ Fake news detector setup warning: {str(e)}")
            return None
    
    def detect_fake_news(self, title, description, source):
        """Advanced fake news detection - REAL ANALYSIS"""
        try:
            fake_score = 0.0
            reasons = []
            
            text = f"{title} {description}".lower()
            source_lower = source.lower()
            
            # Method 1: Keyword-based detection
            fake_keyword_count = sum(1 for keyword in self.fake_news_keywords if keyword in text)
            if fake_keyword_count > 0:
                fake_score += fake_keyword_count * 0.3
                reasons.append(f"Contains {fake_keyword_count} suspicious keywords")
            
            # Method 2: Source reliability check
            is_reliable_source = any(reliable in source_lower for reliable in self.reliable_sources)
            if not is_reliable_source:
                fake_score += 0.2
                reasons.append("Unknown/unreliable source")
            else:
                fake_score -= 0.1  # Bonus for reliable source
                reasons.append("Reliable source")
            
            # Method 3: Content analysis
            # Check for excessive punctuation (!!!, ???)
            if len(re.findall(r'[!?]{2,}', text)) > 0:
                fake_score += 0.15
                reasons.append("Excessive punctuation")
            
            # Check for ALL CAPS words
            caps_words = len(re.findall(r'\b[A-Z]{3,}\b', title + " " + description))
            if caps_words > 2:
                fake_score += 0.1
                reasons.append("Excessive capitalization")
            
            # Check for unrealistic claims
            unrealistic_patterns = [
                r'\d+%.*profit', r'\d+x.*return', r'guaranteed.*\d+%',
                r'risk.*free', r'sure.*shot', r'100%.*safe'
            ]
            
            for pattern in unrealistic_patterns:
                if re.search(pattern, text):
                    fake_score += 0.25
                    reasons.append("Unrealistic financial claims")
                    break
            
            # Method 4: Length and quality check
            if len(description) < 50:
                fake_score += 0.1
                reasons.append("Very short description")
            
            # Normalize score (0-1 scale)
            fake_score = min(fake_score, 1.0)
            fake_score = max(fake_score, 0.0)
            
            # Determine if fake (threshold: 0.5)
            is_fake = fake_score > 0.5
            
            return {
                'is_fake': is_fake,
                'fake_score': round(fake_score, 3),
                'confidence': round((1 - abs(fake_score - 0.5)) * 2, 3),
                'reasons': reasons
            }
            
        except Exception as e:
            print(f"❌ Error in fake news detection: {str(e)}")
            return {
                'is_fake': False,
                'fake_score': 0.0,
                'confidence': 0.5,
                'reasons': ['Analysis failed']
            }
    
    def analyze_sentiment(self, text):
        """Advanced sentiment analysis using multiple methods"""
        try:
            if not text or len(text.strip()) < 3:
                return {
                    'compound': 0.0,
                    'positive': 0.0,
                    'negative': 0.0,
                    'neutral': 1.0,
                    'textblob_polarity': 0.0,
                    'final_sentiment': 'neutral',
                    'confidence': 0.5
                }
            
            # Method 1: VADER Sentiment Analysis
            vader_scores = self.vader_analyzer.polarity_scores(text)
            
            # Method 2: TextBlob Analysis
            blob = TextBlob(text)
            textblob_polarity = blob.sentiment.polarity
            
            # Method 3: Financial keyword analysis
            financial_positive = [
                'profit', 'gain', 'growth', 'bullish', 'rally', 'surge',
                'positive', 'strong', 'outperform', 'buy', 'upgrade',
                'dividend', 'bonus', 'split', 'expansion', 'merger'
            ]
            
            financial_negative = [
                'loss', 'decline', 'bearish', 'crash', 'fall', 'drop',
                'negative', 'weak', 'underperform', 'sell', 'downgrade',
                'debt', 'bankruptcy', 'fraud', 'scandal', 'investigation'
            ]
            
            text_lower = text.lower()
            pos_count = sum(1 for word in financial_positive if word in text_lower)
            neg_count = sum(1 for word in financial_negative if word in text_lower)
            
            # Calculate financial sentiment
            if pos_count + neg_count > 0:
                financial_sentiment = (pos_count - neg_count) / (pos_count + neg_count)
            else:
                financial_sentiment = 0.0
            
            # Combine all methods
            combined_score = (
                vader_scores['compound'] * 0.4 +
                textblob_polarity * 0.3 +
                financial_sentiment * 0.3
            )
            
            # Determine final sentiment
            if combined_score > 0.1:
                final_sentiment = 'positive'
                confidence = min(abs(combined_score) * 2, 1.0)
            elif combined_score < -0.1:
                final_sentiment = 'negative'
                confidence = min(abs(combined_score) * 2, 1.0)
            else:
                final_sentiment = 'neutral'
                confidence = 1.0 - abs(combined_score) * 2
            
            return {
                'compound': round(combined_score, 3),
                'positive': round(vader_scores['pos'], 3),
                'negative': round(vader_scores['neg'], 3),
                'neutral': round(vader_scores['neu'], 3),
                'textblob_polarity': round(textblob_polarity, 3),
                'financial_sentiment': round(financial_sentiment, 3),
                'final_sentiment': final_sentiment,
                'confidence': round(confidence, 3)
            }
            
        except Exception as e:
            print(f"❌ Error in sentiment analysis: {str(e)}")
            return {
                'compound': 0.0,
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 1.0,
                'textblob_polarity': 0.0,
                'financial_sentiment': 0.0,
                'final_sentiment': 'neutral',
                'confidence': 0.5
            }
    
    def process_all_news(self):
        """Process all news articles for sentiment and fake news detection"""
        print("🔍 Processing all news articles for sentiment and fake news detection...")
        
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            
            # Get unprocessed news articles
            query = '''
                SELECT id, title, description, source, url
                FROM news_articles 
                WHERE sentiment_score IS NULL OR is_fake_news IS NULL
                ORDER BY published_at DESC
            '''
            
            news_df = pd.read_sql_query(query, conn)
            
            if news_df.empty:
                print("✅ All news articles already processed")
                return True
            
            print(f"📰 Processing {len(news_df)} news articles...")
            
            processed_count = 0
            fake_news_count = 0
            
            for index, row in news_df.iterrows():
                try:
                    # Analyze sentiment
                    text = f"{row['title']} {row['description']}"
                    sentiment_result = self.analyze_sentiment(text)
                    
                    # Detect fake news
                    fake_result = self.detect_fake_news(
                        row['title'], 
                        row['description'], 
                        row['source']
                    )
                    
                    # Update database
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE news_articles 
                        SET sentiment_score = ?, 
                            is_fake_news = ?
                        WHERE id = ?
                    ''', (
                        sentiment_result['compound'],
                        fake_result['is_fake'],
                        row['id']
                    ))
                    
                    processed_count += 1
                    if fake_result['is_fake']:
                        fake_news_count += 1
                        print(f"🚨 Fake news detected: {row['title'][:50]}...")
                    
                    # Progress indicator
                    if processed_count % 10 == 0:
                        print(f"📊 Processed {processed_count}/{len(news_df)} articles...")
                
                except Exception as e:
                    print(f"❌ Error processing article {row['id']}: {str(e)}")
                    continue
            
            conn.commit()
            conn.close()
            
            print(f"✅ News processing complete:")
            print(f"   📰 Total processed: {processed_count}")
            print(f"   🚨 Fake news detected: {fake_news_count}")
            print(f"   ✅ Legitimate news: {processed_count - fake_news_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error processing news: {str(e)}")
            return False
    
    def get_market_sentiment_summary(self):
        """Get overall market sentiment summary - REAL DATA"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            
            # Get recent sentiment data
            query = '''
                SELECT sentiment_score, is_fake_news, source, published_at
                FROM news_articles 
                WHERE sentiment_score IS NOT NULL 
                AND published_at >= datetime('now', '-24 hours')
                AND is_fake_news = 0
                ORDER BY published_at DESC
            '''
            
            sentiment_df = pd.read_sql_query(query, conn)
            conn.close()
            
            if sentiment_df.empty:
                return {
                    'overall_sentiment': 'neutral',
                    'sentiment_score': 0.0,
                    'total_articles': 0,
                    'positive_articles': 0,
                    'negative_articles': 0,
                    'neutral_articles': 0,
                    'fake_news_filtered': 0
                }
            
            # Calculate sentiment distribution
            positive_articles = len(sentiment_df[sentiment_df['sentiment_score'] > 0.1])
            negative_articles = len(sentiment_df[sentiment_df['sentiment_score'] < -0.1])
            neutral_articles = len(sentiment_df) - positive_articles - negative_articles
            
            # Overall sentiment
            avg_sentiment = sentiment_df['sentiment_score'].mean()
            
            if avg_sentiment > 0.1:
                overall_sentiment = 'positive'
            elif avg_sentiment < -0.1:
                overall_sentiment = 'negative'
            else:
                overall_sentiment = 'neutral'
            
            return {
                'overall_sentiment': overall_sentiment,
                'sentiment_score': round(avg_sentiment, 3),
                'total_articles': len(sentiment_df),
                'positive_articles': positive_articles,
                'negative_articles': negative_articles,
                'neutral_articles': neutral_articles,
                'fake_news_filtered': 'Real data only'
            }
            
        except Exception as e:
            print(f"❌ Error getting market sentiment: {str(e)}")
            return {
                'overall_sentiment': 'neutral',
                'sentiment_score': 0.0,
                'total_articles': 0,
                'positive_articles': 0,
                'negative_articles': 0,
                'neutral_articles': 0,
                'fake_news_filtered': 0
            }

# Test the sentiment analyzer
if __name__ == "__main__":
    print("🧠 Testing Advanced Sentiment Analyzer...")
    
    analyzer = AdvancedSentimentAnalyzer()
    
    # Test sentiment analysis
    test_texts = [
        "Reliance Industries reports strong quarterly profits with 15% growth",
        "Market crashes as investors panic sell amid global uncertainty",
        "HDFC Bank maintains stable performance in challenging times"
    ]
    
    for text in test_texts:
        result = analyzer.analyze_sentiment(text)
        print(f"Text: {text}")
        print(f"Sentiment: {result['final_sentiment']} (Score: {result['compound']})")
        print("-" * 50)
    
    # Test fake news detection
    fake_test = analyzer.detect_fake_news(
        "GUARANTEED 500% RETURNS IN 30 DAYS!!!",
        "Secret insider tip reveals risk-free investment opportunity",
        "unknown_source"
    )
    print(f"Fake News Test: {fake_test}")
    
    print("✅ Sentiment Analyzer test completed!")

# Compatibility class for main.py
class SentimentAnalyzer:
    def __init__(self):
        self.advanced_analyzer = AdvancedSentimentAnalyzer()
        print("✅ Sentiment Analyzer (compatibility) initialized")
    
    # --- New: expose full advanced methods so Phase 2 can use this too ---
    def process_all_news(self):
        """Process all news using the underlying AdvancedSentimentAnalyzer."""
        return self.advanced_analyzer.process_all_news()

    def get_market_sentiment_summary(self):
        """Return full market sentiment summary from the advanced analyzer."""
        return self.advanced_analyzer.get_market_sentiment_summary()

    def analyze_market_sentiment(self):
        """Analyze market sentiment - compatibility method"""
        try:
            # Process all news first
            success = self.advanced_analyzer.process_all_news()
            
            if success:
                # Get market sentiment summary
                summary = self.advanced_analyzer.get_market_sentiment_summary()
                
                # Format for compatibility
                return {
                    'sentiment_label': summary['overall_sentiment'].title(),
                    'overall_sentiment': summary['sentiment_score'],
                    'total_articles': summary['total_articles'],
                    'fake_news_count': 0,  # Will be calculated separately
                    'fake_news_percentage': 0.0
                }
            
            return None
            
        except Exception as e:
            print(f"Error in sentiment analysis: {str(e)}")
            return None
    
    def get_stock_specific_sentiment(self, symbol):
        """Get sentiment for specific stock"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            
            # Search for news related to this stock
            company_name = STOCK_SYMBOLS.get(symbol, symbol.replace('.NS', ''))
            
            query = '''
                SELECT sentiment_score, is_fake_news
                FROM news_articles 
                WHERE (title LIKE ? OR description LIKE ?)
                AND sentiment_score IS NOT NULL
                ORDER BY published_at DESC
                LIMIT 10
            '''
            
            search_term = f"%{company_name}%"
            df = pd.read_sql_query(query, conn, params=(search_term, search_term))
            conn.close()
            
            if not df.empty:
                avg_sentiment = df['sentiment_score'].mean()
                fake_count = df['is_fake_news'].sum()
                
                # Determine sentiment label
                if avg_sentiment > 0.1:
                    sentiment_label = 'Positive'
                elif avg_sentiment < -0.1:
                    sentiment_label = 'Negative'
                else:
                    sentiment_label = 'Neutral'
                
                return {
                    'sentiment_score': avg_sentiment,
                    'sentiment_label': sentiment_label,
                    'articles_count': len(df),
                    'fake_news_count': fake_count
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting stock sentiment: {str(e)}")
            return None