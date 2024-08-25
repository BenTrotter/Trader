# alpaca_trading_bot.py
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import REST, TimeFrame
import numpy as np
import pandas as pd
import time
from dotenv import load_dotenv
import os

load_dotenv()
# Alpaca API credentials
API_KEY = os.getenv('ALPACA_API_KEY')
SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
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
    print(f"\nSMA_9: {data['SMA_9'].iloc[-1]}")
    print(f"SMA_21: {data['SMA_21'].iloc[-1]}")
    print(f"Price: {data['close'].iloc[-1]}")

    if data['SMA_9'].iloc[-1] > data['SMA_21'].iloc[-1]:
        return 'buy'
    elif data['SMA_9'].iloc[-1] < data['SMA_21'].iloc[-1]:
        return 'sell'
    return 'hold'

def trade_stock(ticker, position_ticker):
    """
    Stream live data and trade stock using Alpaca API.
    Args:
        ticker (str): The stock ticker symbol to trade.
    """
    position_manual = False
    while True:
        try:
            bars = api.get_crypto_bars(ticker, TimeFrame.Minute).df

            # Inspect the structure of the DataFrame
            print("Columns:", bars.columns)
            print("Sample Data:\n", bars.tail())

            # Convert the returned data to DataFrame
            if 'close' not in bars.columns:
                raise ValueError("Expected 'close' column not found in the data")

            data = pd.DataFrame({
                'close': bars['close']
            })
            
            signal = moving_average_crossover_strategy(data)

            
            # position = api.list_positions()
            # position = next((pos for pos in position if pos.symbol == position_ticker), None)
            
            print(f"Signal: {signal}\nPosition: {position_manual}\n")

            if signal == 'buy' and not position_manual:
                api.submit_order(
                    symbol=position_ticker,
                    qty=0.001,  # Number of shares to buy
                    side='buy',
                    type='market',
                    time_in_force='gtc'
                )
                print(f"Bought 0.001 shares of {ticker}")


            elif signal == 'sell' and position_manual:
                api.submit_order(
                    symbol=position_ticker,
                    qty=0.001,  # Number of shares to sell
                    side='sell',
                    type='market',
                    time_in_force='gtc'
                )
                print(f"Sold 0.001 shares of {ticker}")

        except Exception as e:
            print(f"An error occurred: {e}")
        
        time.sleep(60)  # Run every minute

if __name__ == "__main__":
    # Example ticker to trade
    position_ticker = "BTCUSD"
    selected_ticker = "BTC/USD"
    trade_stock(selected_ticker, position_ticker)