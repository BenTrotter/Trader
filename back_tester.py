# backtest_strategy.py
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

def fetch_historical_data(ticker):
    """
    Fetches historical stock data for a given ticker.
    Args:
        ticker (str): The stock ticker symbol.
    Returns:
        pd.DataFrame: DataFrame with historical stock data.
    """
    return yf.download(ticker, period='6mo', interval='5m')

def moving_average_crossover_strategy(data):
    """
    Simple moving average crossover strategy.
    Args:
        data (pd.DataFrame): Historical stock data.
    Returns:
        pd.DataFrame: DataFrame with buy/sell signals.
    """
    data['SMA_9'] = data['Close'].rolling(window=9).mean()
    data['SMA_21'] = data['Close'].rolling(window=21).mean()
    
    data['Signal'] = 0
    data['Signal'][9:] = np.where(data['SMA_9'][9:] > data['SMA_21'][9:], 1, -1)
    data['Position'] = data['Signal'].diff()
    
    return data

def backtest_strategy(ticker):
    """
    Backtests the trading strategy on historical data.
    Args:
        ticker (str): The stock ticker symbol to test.
    """
    # Fetch data
    data = fetch_historical_data(ticker)
    
    # Apply strategy
    strategy_data = moving_average_crossover_strategy(data)
    
    # Plot results
    plt.figure(figsize=(14,7))
    plt.plot(data['Close'], label='Close Price')
    plt.plot(data['SMA_9'], label='9-period SMA')
    plt.plot(data['SMA_21'], label='21-period SMA')
    
    plt.plot(strategy_data[strategy_data['Position'] == 1].index, 
             strategy_data['SMA_9'][strategy_data['Position'] == 1],
             '^', markersize=10, color='g', lw=0, label='Buy Signal')

    plt.plot(strategy_data[strategy_data['Position'] == -1].index, 
             strategy_data['SMA_9'][strategy_data['Position'] == -1],
             'v', markersize=10, color='r', lw=0, label='Sell Signal')
    
    plt.title(f'Backtesting {ticker} Strategy')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    ticker = 'AAPL'
    backtest_strategy(ticker)
