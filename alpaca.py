# alpaca_trading_bot.py
import alpaca_trade_api as tradeapi
import numpy as np
import pandas as pd
import time

# Alpaca API credentials
API_KEY = 'YOUR_ALPACA_API_KEY'
SECRET_KEY = 'YOUR_ALPACA_SECRET_KEY'
BASE_URL = 'https://paper-api.alpaca.markets'

api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

def moving_average_crossover_strategy(data):
    """
    Simple moving average crossover strategy for live trading.
    Args:
        data (pd.DataFrame): Historical stock data.
    Returns:
        str: 'buy' or 'sell' based on strategy.
    """
    data['SMA_9'] = data['close'].rolling(window=9).mean()
    data['SMA_21'] = data['close'].rolling(window=21).mean()
    
    if data['SMA_9'].iloc[-1] > data['SMA_21'].iloc[-1]:
        return 'buy'
    elif data['SMA_9'].iloc[-1] < data['SMA_21'].iloc[-1]:
        return 'sell'
    return 'hold'

def trade_stock(ticker):
    """
    Stream live data and trade stock using Alpaca API.
    Args:
        ticker (str): The stock ticker symbol to trade.
    """
    while True:
        barset = api.get_barset(ticker, 'minute', limit=21)
        bars = barset[ticker]
        
        data = pd.DataFrame({
            'close': [bar.c for bar in bars]
        })
        
        signal = moving_average_crossover_strategy(data)
        
        position = api.get_position(ticker) if ticker in [pos.symbol for pos in api.list_positions()] else None
        
        if signal == 'buy' and not position:
            api.submit_order(
                symbol=ticker,
                qty=10,  # Number of shares to buy
                side='buy',
                type='market',
                time_in_force='gtc'
            )
            print(f"Bought 10 shares of {ticker}")

        elif signal == 'sell' and position:
            api.submit_order(
                symbol=ticker,
                qty=10,  # Number of shares to sell
                side='sell',
                type='market',
                time_in_force='gtc'
            )
            print(f"Sold 10 shares of {ticker}")

        time.sleep(60)  # Run every minute

if __name__ == "__main__":
    # Example ticker to trade
    selected_ticker = 'AAPL'
    trade_stock(selected_ticker)
