"""
Advanced stock analysis with multiple API support.
Uses Yahoo Finance, Alpha Vantage, and Polygon.io.
"""

import yfinance as yf
import pandas as pd
import requests
from typing import Dict, List, Optional
import json
from datetime import datetime, timedelta
import time

class AdvancedStockAnalyzer:
    """
    Multi-API stock analyzer with technical indicators.
    Supports Yahoo Finance, Alpha Vantage, and Polygon.io.
    """
    
    STOCKS = {
        'META': 'Meta (Facebook)',
        'AAPL': 'Apple',
        'AMZN': 'Amazon',
        'NFLX': 'Netflix',
        'GOOGL': 'Google (Alphabet)',
        'MSFT': 'Microsoft',
        'NVDA': 'NVIDIA',
        'UBER': 'Uber'
    }
    
    def __init__(self, alpha_vantage_key: Optional[str] = None, polygon_key: Optional[str] = None):
        """Initialize with optional API keys for enhanced data"""
        self.alpha_vantage_key = alpha_vantage_key
        self.polygon_key = polygon_key
    
    def fetch_yahoo_data(self, symbol: str, period: str = '1y') -> pd.DataFrame:
        """Gets data from Yahoo Finance"""
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period=period)
            return df
        except Exception as e:
            print(f"Yahoo Finance error for {symbol}: {e}")
            return pd.DataFrame()
    
    def fetch_alpha_vantage_data(self, symbol: str) -> Dict:
        """Gets data from Alpha Vantage (25 req/day, 5 req/min)"""
        if not self.alpha_vantage_key:
            return {'error': 'No API key provided'}
        
        try:
            url = f'https://www.alphavantage.co/query'
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': self.alpha_vantage_key,
                'outputsize': 'full'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'Error Message' in data:
                return {'error': data['Error Message']}
            
            if 'Note' in data:
                return {'error': 'API rate limit reached'}
            
            return data
        except Exception as e:
            return {'error': str(e)}
    
    def fetch_polygon_data(self, symbol: str, days: int = 365) -> Dict:
        """Gets data from Polygon.io (5 calls/min)"""
        if not self.polygon_key:
            return {'error': 'No API key provided'}
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            url = f'https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start_date.strftime("%Y-%m-%d")}/{end_date.strftime("%Y-%m-%d")}'
            params = {
                'apiKey': self.polygon_key,
                'adjusted': 'true',
                'sort': 'asc'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            return data
        except Exception as e:
            return {'error': str(e)}
    
    def calculate_moving_averages(self, df: pd.DataFrame, periods: List[int]) -> Dict:
        """Calculates MAs and price position relative to each"""
        if df.empty:
            return {}
        
        averages = {}
        for period in periods:
            if len(df) >= period:
                ma = df['Close'].rolling(window=period).mean()
                averages[f'{period}d_MA'] = round(ma.iloc[-1], 2)
                
                current_price = df['Close'].iloc[-1]
                diff = round(((current_price - ma.iloc[-1]) / ma.iloc[-1]) * 100, 2)
                averages[f'{period}d_MA_diff_%'] = diff
            else:
                averages[f'{period}d_MA'] = None
                averages[f'{period}d_MA_diff_%'] = None
        
        return averages
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculates RSI, volatility, and other indicators"""
        if df.empty or len(df) < 20:
            return {}
        
        indicators = {}
        
        # 14-day RSI
        if len(df) >= 14:
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            indicators['RSI_14'] = round(rsi.iloc[-1], 2)
        
        returns = df['Close'].pct_change()
        indicators['volatility_30d'] = round(returns.tail(30).std() * 100, 2)
        indicators['avg_volume_30d'] = int(df['Volume'].tail(30).mean())
        
        # 52-week range
        if len(df) >= 252:
            indicators['52w_high'] = round(df['Close'].tail(252).max(), 2)
            indicators['52w_low'] = round(df['Close'].tail(252).min(), 2)
        
        return indicators
    
    def analyze_stock_comprehensive(self, symbol: str) -> Dict:
        """Full analysis using all available data sources"""
        print(f"Analyzing {symbol} - {self.STOCKS.get(symbol, 'Unknown')}...")
        
        analysis = {
            'symbol': symbol,
            'name': self.STOCKS.get(symbol, 'Unknown'),
            'timestamp': datetime.now().isoformat()
        }
        
        df = self.fetch_yahoo_data(symbol, period='1y')
        
        if not df.empty:
            latest = df.iloc[-1]
            analysis['current_stats'] = {
                'current_price': round(latest['Close'], 2),
                'open': round(latest['Open'], 2),
                'high': round(latest['High'], 2),
                'low': round(latest['Low'], 2),
                'volume': int(latest['Volume']),
                'date': latest.name.strftime('%Y-%m-%d')
            }
            
            ma_periods = [15, 30, 50, 100, 200]
            analysis['moving_averages'] = self.calculate_moving_averages(df, ma_periods)
            analysis['technical_indicators'] = self.calculate_technical_indicators(df)
            
            # Price change percentages
            price_changes = {}
            for days in [1, 5, 15, 30, 90]:
                if len(df) >= days:
                    old_price = df['Close'].iloc[-days]
                    current_price = analysis['current_stats']['current_price']
                    change = round(((current_price - old_price) / old_price) * 100, 2)
                    price_changes[f'{days}d_change_%'] = change
            
            analysis['price_changes'] = price_changes
        else:
            analysis['error'] = 'Failed to fetch Yahoo Finance data'
        
        if self.alpha_vantage_key:
            print(f"  Fetching Alpha Vantage data...")
            av_data = self.fetch_alpha_vantage_data(symbol)
            analysis['alpha_vantage'] = av_data.get('Meta Data', {}) if 'error' not in av_data else av_data
            time.sleep(12)
        
        if self.polygon_key:
            print(f"  Fetching Polygon.io data...")
            polygon_data = self.fetch_polygon_data(symbol)
            if 'results' in polygon_data:
                analysis['polygon_data_points'] = len(polygon_data['results'])
            elif 'error' in polygon_data:
                analysis['polygon_error'] = polygon_data['error']
            time.sleep(12)
        
        return analysis
    
    def print_comprehensive_analysis(self, analysis: Dict):
        """Displays formatted analysis with all indicators"""
        print("\n" + "=" * 80)
        print(f"{analysis['symbol']} - {analysis['name']}")
        print("=" * 80)
        
        if 'error' in analysis:
            print(f"Error: {analysis['error']}")
            return
        
        stats = analysis.get('current_stats', {})
        if stats:
            print(f"\nCurrent Stats (as of {stats['date']}):")
            print(f"  Price: ${stats['current_price']}")
            print(f"  Open: ${stats['open']} | High: ${stats['high']} | Low: ${stats['low']}")
            print(f"  Volume: {stats['volume']:,}")
        
        ma = analysis.get('moving_averages', {})
        if ma:
            print(f"\nMoving Averages & Position:")
            for period in [15, 30, 50, 100, 200]:
                ma_val = ma.get(f'{period}d_MA')
                ma_diff = ma.get(f'{period}d_MA_diff_%')
                if ma_val and ma_diff is not None:
                    position = "above" if ma_diff > 0 else "below"
                    print(f"  {period}-day MA: ${ma_val} ({ma_diff:+.2f}% {position})")
        
        tech = analysis.get('technical_indicators', {})
        if tech:
            print(f"\nTechnical Indicators:")
            if 'RSI_14' in tech:
                rsi = tech['RSI_14']
                rsi_signal = "Oversold" if rsi < 30 else "Overbought" if rsi > 70 else "Neutral"
                print(f"  RSI (14-day): {rsi} ({rsi_signal})")
            if 'volatility_30d' in tech:
                print(f"  30-day Volatility: {tech['volatility_30d']}%")
            if 'avg_volume_30d' in tech:
                print(f"  Avg Volume (30d): {tech['avg_volume_30d']:,}")
            if '52w_high' in tech and '52w_low' in tech:
                print(f"  52-Week Range: ${tech['52w_low']} - ${tech['52w_high']}")
        
        changes = analysis.get('price_changes', {})
        if changes:
            print(f"\nPrice Changes:")
            for period, change in sorted(changes.items()):
                days = period.split('d')[0]
                print(f"  {days}-day: {change:+.2f}%")
        
        print()


def main():
    """Runs advanced analysis with technical indicators"""
    print("Advanced Tech Stock Analyzer")
    print("=" * 80)
    print()
    
    
    analyzer = AdvancedStockAnalyzer()
    
   
    results = {}
    for symbol in analyzer.STOCKS.keys():
        results[symbol] = analyzer.analyze_stock_comprehensive(symbol)
        analyzer.print_comprehensive_analysis(results[symbol])
    
    with open('advanced_stock_analysis.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to advanced_stock_analysis.json")


if __name__ == "__main__":
    main()
