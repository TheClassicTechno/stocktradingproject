# FAANG + Microsoft + NVIDIA + Uber Stock Analysis Tool

A comprehensive Python tool to analyze stocks from FAANG companies (Meta, Apple, Amazon, Netflix, Google) plus Microsoft, NVIDIA, and Uber using multiple stock market APIs.

## Features

- **Real-time stock data** from Yahoo Finance
- **Moving averages** calculation (15, 30, 50, 100, 200 days)
- **Technical indicators** (RSI, Volatility, 52-week high/low)
- **Price change tracking** (1, 5, 15, 30, 90 days)
- **Multiple API support**:
  - Yahoo Finance (free, no API key needed)
  - Alpha Vantage (optional, free tier available)
  - Polygon.io (optional, free tier available)
- **JSON export** analysis results
- **Summary comparison** across all stocks
- **Visualizations** with charts and graphs


## Stock Symbols Analyzed

- **META** - Meta (Facebook)
- **AAPL** - Apple
- **AMZN** - Amazon
- **NFLX** - Netflix
- **GOOGL** - Google (Alphabet)
- **MSFT** - Microsoft
- **NVDA** - NVIDIA
- **UBER** - Uber


## Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run basic analysis
python stock_analyzer.py

# Generate visualizations
python visualizer.py
```

RSI (Relative Strength Index):
  - Below 30 = Oversold (potential buy signal)
  - Above 70 = Overbought (potential sell signal)
  - 30-70 = Neutral zone

## Future Enhancements

- Add data visualization with interactive charts
- Implement portfolio tracking
- Add email alerts for price targets
- Include fundamental analysis (P/E ratios, earnings, etc.)
- Add machine learning predictions
- Real-time streaming data

## License

MIT License