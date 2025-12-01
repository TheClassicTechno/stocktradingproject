"""
Stock comparison and ranking tool.
Compares performance and trends across multiple stocks.
"""

import json
from datetime import datetime
from typing import Dict, List, Tuple

class StockComparator:
    """Handles stock comparison and ranking"""
    
    def __init__(self, json_file: str = 'stock_analysis.json'):
        """Loads analysis data from JSON"""
        try:
            with open(json_file, 'r') as f:
                self.data = json.load(f)
            print(f"Loaded data for {len(self.data)} stocks\n")
        except FileNotFoundError:
            print(f"Error: {json_file} not found. Please run stock_analyzer.py first.")
            self.data = {}
    
    def get_best_performers(self, period: str = '30_day_change_%') -> List[Tuple[str, float]]:
        """Returns stocks sorted by performance"""
        performances = []
        for symbol, data in self.data.items():
            if 'price_changes' in data and period in data['price_changes']:
                change = data['price_changes'][period]
                if change is not None:
                    performances.append((symbol, change))
        
        return sorted(performances, key=lambda x: x[1], reverse=True)
    
    def analyze_trend_strength(self, symbol: str) -> Dict:
        """Calculates trend strength from MA positioning"""
        if symbol not in self.data:
            return {}
        
        stock = self.data[symbol]
        if 'current_stats' not in stock or 'moving_averages' not in stock:
            return {}
        
        price = stock['current_stats']['current_price']
        ma = stock['moving_averages']
        
        above_below = {}
        for ma_name, ma_value in ma.items():
            if ma_value and 'd_MA' in ma_name:
                above_below[ma_name] = price > ma_value
        
        above_count = sum(1 for v in above_below.values() if v)
        total_count = len(above_below)
        
        trend_strength = (above_count / total_count * 100) if total_count > 0 else 0
        
        if trend_strength >= 80:
            trend = "Strong Bullish"
        elif trend_strength >= 60:
            trend = "Moderately Bullish"
        elif trend_strength >= 40:
            trend = "Neutral"
        elif trend_strength >= 20:
            trend = "Moderately Bearish"
        else:
            trend = "Strong Bearish"
        
        return {
            'trend': trend,
            'strength_score': round(trend_strength, 1),
            'above_mas': above_count,
            'total_mas': total_count
        }
    
    def get_momentum_score(self, symbol: str) -> float:
        """Calculates weighted momentum from recent changes"""
        if symbol not in self.data or 'price_changes' not in self.data[symbol]:
            return 0.0
        
        changes = self.data[symbol]['price_changes']
        
        weights = {
            '15_day_change_%': 0.4,
            '30_day_change_%': 0.6
        }
        
        score = 0
        total_weight = 0
        
        for period, weight in weights.items():
            if period in changes and changes[period] is not None:
                score += changes[period] * weight
                total_weight += weight
        
        return round(score / total_weight if total_weight > 0 else 0, 2)
    
    def generate_report(self):
        """Generates and displays comparison report"""
        if not self.data:
            print("No data available. Please run stock_analyzer.py first.")
            return
        
        print("=" * 90)
        print(" " * 25 + "STOCK COMPARISON REPORT")
        print("=" * 90)
        print()
        
        print("PERFORMANCE RANKINGS (30-Day Change)")
        print("-" * 90)
        performers = self.get_best_performers('30_day_change_%')
        for i, (symbol, change) in enumerate(performers, 1):
            marker = "+" if change > 0 else "-"
            name = self.data[symbol]['name']
            print(f"  {i}. [{marker}] {symbol:<6} ({name:<20}): {change:+.2f}%")
        print()
        
        print("TREND STRENGTH ANALYSIS")
        print("-" * 90)
        print(f"{'Symbol':<8} {'Name':<20} {'Trend':<20} {'Score':<10} {'Price vs MAs':<15}")
        print("-" * 90)
        
        for symbol in self.data.keys():
            trend_data = self.analyze_trend_strength(symbol)
            if trend_data:
                name = self.data[symbol]['name']
                price = self.data[symbol]['current_stats']['current_price']
                
                print(f"{symbol:<8} {name:<20} {trend_data['trend']:<20} "
                      f"{trend_data['strength_score']:.1f}%{'':<6} "
                      f"{trend_data['above_mas']}/{trend_data['total_mas']} above")
        print()
        
        print("MOMENTUM SCORES")
        print("-" * 90)
        momentum_scores = [(symbol, self.get_momentum_score(symbol)) 
                          for symbol in self.data.keys()]
        momentum_scores.sort(key=lambda x: x[1], reverse=True)
        
        for symbol, score in momentum_scores:
            name = self.data[symbol]['name']
            print(f"  {symbol:<6} ({name:<20}): {score:+.2f} points")
        print()
        
        print("CURRENT PRICES & KEY AVERAGES")
        print("-" * 90)
        print(f"{'Symbol':<8} {'Price':<12} {'15d MA':<12} {'30d MA':<12} {'50d MA':<12} {'200d MA':<12}")
        print("-" * 90)
        
        for symbol, data in self.data.items():
            if 'current_stats' in data and 'moving_averages' in data:
                price = data['current_stats']['current_price']
                ma = data['moving_averages']
                
                print(f"{symbol:<8} ${price:<11.2f} "
                      f"${ma.get('15d_MA', 0):<11.2f} "
                      f"${ma.get('30d_MA', 0):<11.2f} "
                      f"${ma.get('50d_MA', 0):<11.2f} "
                      f"${ma.get('200d_MA', 0):<11.2f}")
        print()
        
        print("KEY INSIGHTS")
        print("-" * 90)
        
        if performers:
            best = performers[0]
            print(f"  Best Performer: {best[0]} with {best[1]:+.2f}% gain over 30 days")
        
        if performers:
            worst = performers[-1]
            print(f"  Weakest Performer: {worst[0]} with {worst[1]:+.2f}% change over 30 days")
        
        if momentum_scores:
            highest_momentum = momentum_scores[0]
            print(f"  Highest Momentum: {highest_momentum[0]} with score of {highest_momentum[1]:+.2f}")
        
        strong_bullish = [symbol for symbol in self.data.keys() 
                         if self.analyze_trend_strength(symbol).get('strength_score', 0) >= 80]
        if strong_bullish:
            print(f"  Strong Bullish Trends: {', '.join(strong_bullish)}")
        
        bearish = [symbol for symbol in self.data.keys() 
                  if self.analyze_trend_strength(symbol).get('strength_score', 0) < 40]
        if bearish:
            print(f"  Below Most MAs: {', '.join(bearish)}")
        
        print()
        print("=" * 90)
        print("Disclaimer: This is for educational purposes only. Not financial advice.")
        print("=" * 90)
    
    def export_comparison(self, filename: str = 'stock_comparison.txt'):
        """Saves report to text file"""
        import sys
        from io import StringIO
        
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        self.generate_report()
        
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        with open(filename, 'w') as f:
            f.write(output)
        
        print(f"\nComparison report exported to {filename}")


def main():
    """Runs comparison and displays report"""
    comparator = StockComparator()
    
    if comparator.data:
        comparator.generate_report()
        
        # Optional export
        print("\nWould you like to export this report to a text file? (y/n): ", end='')
        try:
            response = input().lower().strip()
            if response == 'y':
                comparator.export_comparison()
        except:
            pass


if __name__ == "__main__":
    main()
