"""
Stock analysis tool for tracking tech stocks.
Pulls data from Yahoo Finance and calculates moving averages.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests
from typing import Dict, List
import json

class StockAnalyzer:
    """Handles stock data fetching and analysis"""
    
    # Tech stocks to track
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
    
    def __init__(self):
        self.data = {}
        
    def fetch_stock_data(self, symbol: str, period: str = '3mo') -> pd.DataFrame:
        """Gets historical stock data for the given period"""
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period=period)
            return df
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_moving_averages(self, df: pd.DataFrame, periods: List[int] = [15, 30, 50, 100, 200]) -> Dict:
        """Calculates moving averages for specified periods"""
        if df.empty:
            return {}
        
        averages = {}
        for period in periods:
            if len(df) >= period:
                ma = df['Close'].rolling(window=period).mean()
                averages[f'{period}d_MA'] = round(ma.iloc[-1], 2)
            else:
                averages[f'{period}d_MA'] = None
        
        return averages
    
    def get_current_stats(self, df: pd.DataFrame) -> Dict:
        """Returns latest price, volume, and trading stats"""
        if df.empty:
            return {}
        
        latest = df.iloc[-1]
        stats = {
            'current_price': round(latest['Close'], 2),
            'open': round(latest['Open'], 2),
            'high': round(latest['High'], 2),
            'low': round(latest['Low'], 2),
            'volume': int(latest['Volume']),
            'date': latest.name.strftime('%Y-%m-%d')
        }
        
        return stats
    
    def analyze_stock(self, symbol: str) -> Dict:
        """Runs full analysis including MAs and price changes"""
        print(f"Analyzing {symbol} - {self.STOCKS.get(symbol, 'Unknown')}...")
        
        # Get 1 year of data for 200-day moving average
        df = self.fetch_stock_data(symbol, period='1y')
        
        if df.empty:
            return {'error': 'Failed to fetch data'}
        
        stats = self.get_current_stats(df)
        ma_periods = [15, 30, 50, 100, 200]
        moving_averages = self.calculate_moving_averages(df, ma_periods)
        
        # Price changes over time
        if len(df) >= 30:
            price_30d_ago = df['Close'].iloc[-30]
            change_30d = round(((stats['current_price'] - price_30d_ago) / price_30d_ago) * 100, 2)
        else:
            change_30d = None
        
        if len(df) >= 15:
            price_15d_ago = df['Close'].iloc[-15]
            change_15d = round(((stats['current_price'] - price_15d_ago) / price_15d_ago) * 100, 2)
        else:
            change_15d = None
        
        analysis = {
            'symbol': symbol,
            'name': self.STOCKS.get(symbol, 'Unknown'),
            'current_stats': stats,
            'moving_averages': moving_averages,
            'price_changes': {
                '15_day_change_%': change_15d,
                '30_day_change_%': change_30d
            }
        }
        
        return analysis
    
    def analyze_all_stocks(self) -> Dict:
        """Runs analysis on all tracked stocks"""
        results = {}
        
        for symbol in self.STOCKS.keys():
            results[symbol] = self.analyze_stock(symbol)
            print()
        
        return results
    
    def print_analysis(self, analysis: Dict):
        """Displays formatted analysis results"""
        print("=" * 80)
        print(f"{analysis['symbol']} - {analysis['name']}")
        print("=" * 80)
        
        if 'error' in analysis:
            print(f"Error: {analysis['error']}")
            return
        
        stats = analysis['current_stats']
        print(f"\nCurrent Stats (as of {stats['date']}):")
        print(f"  Current Price: ${stats['current_price']}")
        print(f"  Open: ${stats['open']}")
        print(f"  High: ${stats['high']}")
        print(f"  Low: ${stats['low']}")
        print(f"  Volume: {stats['volume']:,}")
        
        print(f"\nMoving Averages:")
        for ma_name, ma_value in analysis['moving_averages'].items():
            if ma_value:
                print(f"  {ma_name}: ${ma_value}")
            else:
                print(f"  {ma_name}: Insufficient data")
        
        print(f"\nPrice Changes:")
        changes = analysis['price_changes']
        if changes['15_day_change_%']:
            print(f"  15-Day Change: {changes['15_day_change_%']:+.2f}%")
        if changes['30_day_change_%']:
            print(f"  30-Day Change: {changes['30_day_change_%']:+.2f}%")
        
        print()
    
    def save_to_json(self, results: Dict, filename: str = 'stock_analysis.json'):
        """Saves results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results saved to {filename}")


def main():
    """Runs the stock analysis and displays results"""
    print("Tech Stock Analyzer")
    print("=" * 80)
    print()
    
    analyzer = StockAnalyzer()
    results = analyzer.analyze_all_stocks()
    
    # Show detailed results
    print("\n" + "=" * 80)
    print("DETAILED ANALYSIS")
    print("=" * 80 + "\n")
    
    for symbol, analysis in results.items():
        analyzer.print_analysis(analysis)
    
    analyzer.save_to_json(results)
    
    # Summary table
    print("\n" + "=" * 80)
    print("SUMMARY COMPARISON")
    print("=" * 80)
    print(f"\n{'Symbol':<10} {'Current Price':<15} {'15d MA':<12} {'30d MA':<12} {'30d Change':<12}")
    print("-" * 80)
    
    for symbol, analysis in results.items():
        if 'error' not in analysis:
            stats = analysis['current_stats']
            ma = analysis['moving_averages']
            changes = analysis['price_changes']
            
            ma_15 = f"${ma.get('15d_MA', 'N/A')}" if ma.get('15d_MA') else "N/A"
            ma_30 = f"${ma.get('30d_MA', 'N/A')}" if ma.get('30d_MA') else "N/A"
            change_30 = f"{changes['30_day_change_%']:+.2f}%" if changes['30_day_change_%'] else "N/A"
            
            print(f"{symbol:<10} ${stats['current_price']:<14.2f} {ma_15:<12} {ma_30:<12} {change_30:<12}")


if __name__ == "__main__":
    main()
