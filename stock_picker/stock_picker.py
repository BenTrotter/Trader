import yfinance as yf
import pandas as pd
import numpy as np
import datetime as dt
from ta.momentum import RSIIndicator
from ta.trend import MACD
from sklearn.preprocessing import MinMaxScaler
from stock_picker_tickers import SP500_TICKERS

# todo this should use all stock picker classes and produce a dashboard print out in the terminal

# Step 1: Fetch Historical Data
def fetch_stock_data(tickers, start_date, end_date):
    data = {}
    for ticker in tickers:
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        data[ticker] = stock_data
    return data

# Step 2: Calculate Technical Indicators
def calculate_indicators(data):
    indicators = {}
    for ticker, df in data.items():
        df['RSI'] = RSIIndicator(df['Close']).rsi()
        macd = MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_signal'] = macd.macd_signal()
        indicators[ticker] = df
    return indicators

# Step 3: Strategy to Select Stocks
def select_stocks(indicators):
    selected_stocks = []
    for ticker, df in indicators.items():
        # Use RSI and MACD for a simple strategy
        if df['RSI'].iloc[-1] > 50 and df['MACD'].iloc[-1] > df['MACD_signal'].iloc[-1]:
            selected_stocks.append(ticker)
    return selected_stocks

# Step 4: Main Function to Run Before Market Opens
def main():
    
    # Define the date range for historical data
    end_date = dt.datetime.today() - dt.timedelta(days=1) # todo this minus one is just for testing 
    start_date = end_date - dt.timedelta(days=90)  # Last 3 months of data
    
    # Fetch historical data
    data = fetch_stock_data(SP500_TICKERS, start_date, end_date)
    
    # Calculate technical indicators
    indicators = calculate_indicators(data)
    
    # Select stocks based on strategy
    stocks_to_trade = select_stocks(indicators)
    
    if stocks_to_trade:
        print(f"Stocks to consider for day trading today: {stocks_to_trade}")
    else:
        print("No suitable stocks found for day trading today.")

if __name__ == "__main__":
    main()
