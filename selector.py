# stock_selector.py
import yfinance as yf
import pandas_ta as ta
import numpy as np

def select_stock():
    """
    Selects a stock to trade for the day based on fundamental and technical analysis.
    Returns:
        str: A ticker symbol suitable for day trading.
    """
    # Step 1: Define a list of potential stocks (for example, S&P 500 stocks)
    # For simplicity, we'll use a smaller subset
    potential_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'FB', 'TSLA']
    
    selected_stock = None
    for ticker in potential_stocks:
        # Fetch historical data
        stock_data = yf.download(ticker, period='1y', interval='1d')
        
        # Step 2: Perform technical analysis
        # Calculate moving averages
        stock_data['SMA_50'] = ta.sma(stock_data['Close'], length=50)
        stock_data['SMA_200'] = ta.sma(stock_data['Close'], length=200)
        
        # Check for uptrend: SMA 50 should be above SMA 200
        if stock_data['SMA_50'].iloc[-1] > stock_data['SMA_200'].iloc[-1]:
            selected_stock = ticker
            break  # Select the first stock meeting criteria
        else:
            print("No stocks meets the criteria")
    return selected_stock

if __name__ == "__main__":
    selected_ticker = select_stock()
    print(f"Selected Stock for Trading: {selected_ticker}")
