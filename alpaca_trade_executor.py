from alpaca.data.live import StockDataStream, CryptoDataStream
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np  # Make sure to import numpy
from alpaca_functions import *
from trading_session import *
from globals import *

# Load environment variables from .env file
load_dotenv(override=True)

# Alpaca API credentials
API_KEY = os.getenv('ALPACA_API_KEY')
SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')

print(API_KEY)
print(SECRET_KEY)

# Initialize the WebSocket client
if(crypto):
    wss_client = CryptoDataStream(API_KEY, SECRET_KEY)
    ticker = crypto_ticker
elif(stock):
    wss_client = StockDataStream(API_KEY, SECRET_KEY)
    ticker = ticker

# Initialize an empty DataFrame to store incoming bar data
columns = ['symbol', 'timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'trade_count', 'vwap']
growing_df = pd.DataFrame(columns=columns)
growing_df_from_alpaca  = pd.DataFrame(columns=columns)


count = 0

# Start trading session
trading_session = Trading_session(1000)
trade = None

# Async handler to process incoming bar data
async def quote_data_handler(data):
    global growing_df_from_alpaca 
    global growing_df
    global trading_session
    global trade
    global count

    if count == 5 or count == 10 or count == 15 or count == 40:
        print(f"\n\n ****** Displaying from {count} ****** \n\n")
        trading_session.display_trades()
        trading_session.calculate_percentage_change_of_strategy()
        print(trading_session)

    # Convert incoming data to a dictionary
    bar_data = {
        'symbol': data.symbol,
        'timestamp': data.timestamp,
        'Open': data.open,
        'High': data.high,
        'Low': data.low,
        'Close': data.close,
        'Volume': data.volume,
        'trade_count': data.trade_count,
        'vwap': data.vwap
    }

    growing_df_from_alpaca = pd.concat([growing_df_from_alpaca, pd.DataFrame([bar_data])], ignore_index=True)
    copy = growing_df_from_alpaca.copy()

    if(len(copy) > 1): 

        # TODO: Implement growing dataframe using trading strategy v1
        # growing_df = moving_average_crossover_strategy(copy, short_window=1, long_window=2)

        print("\nGrowing DataFrame:\n", growing_df.tail(2))
        print("\n")

        trade, trading_session = analyse_latest_alpaca_bar(trading_session, trade, growing_df.iloc[-1], growing_df['timestamp'].iloc[-1])

        count += 1
        


# Subscribe to minute bar updates for SPY
wss_client.subscribe_bars(quote_data_handler, ticker)


wss_client.run()
