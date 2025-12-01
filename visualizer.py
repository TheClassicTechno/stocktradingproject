"""
Stock data visualization tools.
Generates charts and comparison plots.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import yfinance as yf
from typing import List, Dict
import json

class StockVisualizer:
    """Handles chart generation and visualization"""
    
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
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def plot_stock_with_ma(self, symbol: str, period: str = '6mo', ma_periods: List[int] = [15, 30, 50, 200]):
        """Creates price chart with moving averages overlay"""
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)
        
        if df.empty:
            print(f"No data available for {symbol}")
            return
        
        fig, ax = plt.subplots(figsize=(14, 7))
        ax.plot(df.index, df['Close'], label='Close Price', linewidth=2, color='#1f77b4')
        
        colors = ['#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        for i, period in enumerate(ma_periods):
            if len(df) >= period:
                ma = df['Close'].rolling(window=period).mean()
                ax.plot(df.index, ma, label=f'{period}-day MA', 
                       linewidth=1.5, alpha=0.7, color=colors[i % len(colors)])
        
        ax.set_title(f'{symbol} - {self.STOCKS.get(symbol, "Unknown")} Stock Price with Moving Averages', 
                    fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Price ($)', fontsize=12)
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        filename = f'{symbol}_price_ma.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Chart saved as {filename}")
        
        plt.show()
    
    def plot_volume_analysis(self, symbol: str, period: str = '6mo'):
        """Creates dual chart with price and volume"""
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)
        
        if df.empty:
            print(f"No data available for {symbol}")
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), 
                                        gridspec_kw={'height_ratios': [3, 1]})
        ax1.plot(df.index, df['Close'], linewidth=2, color='#1f77b4')
        ax1.set_title(f'{symbol} - {self.STOCKS.get(symbol, "Unknown")} Price & Volume Analysis', 
                     fontsize=16, fontweight='bold')
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        
        colors = ['#2ca02c' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#d62728' 
                 for i in range(len(df))]
        ax2.bar(df.index, df['Volume'], color=colors, alpha=0.7)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('Volume', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        filename = f'{symbol}_volume_analysis.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Chart saved as {filename}")
        
        plt.show()
    
    def plot_comparison(self, period: str = '6mo'):
        """Creates normalized performance comparison"""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
        
        for i, (symbol, name) in enumerate(self.STOCKS.items()):
            stock = yf.Ticker(symbol)
            df = stock.history(period=period)
            
            if not df.empty:
                normalized = (df['Close'] / df['Close'].iloc[0] - 1) * 100
                ax.plot(df.index, normalized, label=f'{symbol}', 
                       linewidth=2, color=colors[i])
        
        ax.set_title('Tech Stock Performance Comparison (Normalized)', 
                    fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Return (%)', fontsize=12)
        ax.legend(loc='best', fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        filename = 'stock_comparison.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Chart saved as {filename}")
        
        plt.show()
    
    def plot_ma_summary(self):
        """Creates bar chart comparing prices and MAs"""
        try:
            with open('stock_analysis.json', 'r') as f:
                results = json.load(f)
        except FileNotFoundError:
            print("Please run stock_analyzer.py first to generate analysis data")
            return
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        symbols = list(self.STOCKS.keys())
        ma_periods = ['15d_MA', '30d_MA', '50d_MA']
        
        x = range(len(symbols))
        width = 0.2
        
        for i, ma in enumerate(ma_periods):
            values = []
            for symbol in symbols:
                if symbol in results and 'moving_averages' in results[symbol]:
                    ma_val = results[symbol]['moving_averages'].get(ma)
                    values.append(ma_val if ma_val else 0)
                else:
                    values.append(0)
            
            offset = (i - 1) * width
            ax.bar([xi + offset for xi in x], values, width, 
                  label=ma.replace('d_MA', '-day MA'))
        
        current_prices = []
        for symbol in symbols:
            if symbol in results and 'current_stats' in results[symbol]:
                current_prices.append(results[symbol]['current_stats']['current_price'])
            else:
                current_prices.append(0)
        
        ax.plot(x, current_prices, 'ro-', linewidth=2, markersize=8, 
               label='Current Price')
        
        ax.set_xlabel('Stock Symbol', fontsize=12)
        ax.set_ylabel('Price ($)', fontsize=12)
        ax.set_title('Current Price vs Moving Averages Comparison', 
                    fontsize=16, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(symbols)
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        filename = 'ma_comparison.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Chart saved as {filename}")
        
        plt.show()


def main():
    """Generates all visualization charts"""
    print("Stock Analysis Visualizer")
    print("=" * 80)
    print()
    
    visualizer = StockVisualizer()
    
    print("Generating visualizations...")
    print()
    
    print("1. Creating performance comparison chart...")
    visualizer.plot_comparison(period='6mo')
    print()
    
    print("2. Creating individual stock chart with moving averages (AAPL)...")
    visualizer.plot_stock_with_ma('AAPL', period='6mo', ma_periods=[15, 30, 50, 200])
    print()
    
    print("3. Creating volume analysis chart (MSFT)...")
    visualizer.plot_volume_analysis('MSFT', period='6mo')
    print()
    
    print("4. Creating moving averages comparison...")
    visualizer.plot_ma_summary()
    print()
    
    print("All visualizations completed!")
    print("Charts saved as PNG files in the current directory.")


if __name__ == "__main__":
    main()
