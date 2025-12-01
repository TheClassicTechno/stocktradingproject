#!/usr/bin/env python3
"""
Displays quick portfolio summary.
"""
import json

def display_summary():
    print('\n' + '='*90)
    print(' '*30 + '8-STOCK PORTFOLIO SUMMARY')
    print('='*90)

    with open('stock_analysis.json', 'r') as f:
        data = json.load(f)

    print('\nALL STOCKS AT A GLANCE:\n')
    print(f"{'Symbol':<8} {'Name':<22} {'Price':<12} {'30d Change':<12} {'Trend':<15}")
    print('-'*90)

    for symbol, stock in data.items():
        name = stock['name']
        price = f"${stock['current_stats']['current_price']:.2f}"
        change = stock['price_changes']['30_day_change_%']
        change_str = f"{change:+.2f}%"
        
        ma_30 = stock['moving_averages']['30d_MA']
        current = stock['current_stats']['current_price']
        
        if current > ma_30:
            trend = 'Bullish'
            marker = '+'
        else:
            trend = 'Bearish'
            marker = '-'
        
        new_tag = ' [NEW]' if symbol in ['NVDA', 'UBER'] else ''
        
        print(f'[{marker}] {symbol:<6} {name:<22} {price:<12} {change_str:<12} {trend:<15}{new_tag}')

    print('\n' + '='*90)
    
    winners = sum(1 for s in data.values() if s['price_changes']['30_day_change_%'] > 0)
    losers = len(data) - winners
    
    print(f'Winners: {winners}  |  Losers: {losers}')
    print('Tracking 8 stocks (NVDA & UBER recently added)')
    print('='*90 + '\n')

if __name__ == "__main__":
    display_summary()
