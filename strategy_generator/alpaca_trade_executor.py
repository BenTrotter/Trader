from alpaca.data.live import StockDataStream, CryptoDataStream
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np  # Make sure to import numpy
from alpaca_functions import *
from trading_session import *
from indicator_filter import *
from indicator_setup import *
from indicator_trigger import *
from combined_strategy import combined_strategy
from globals import *

# Load environment variables from .env file
load_dotenv(override=True)

# Alpaca API credentials
API_KEY = os.getenv('ALPACA_PERSONAL_API_KEY_ID')
SECRET_KEY = os.getenv('ALPACA_PERSONAL_API_SECRET_KEY')

print(API_KEY)
print(SECRET_KEY)

# Initialize the WebSocket client
if(CRYPTO):
    wss_client = CryptoDataStream(API_KEY, SECRET_KEY)
    TICKER = CRYPTO_TICKER
elif(STOCK):
    wss_client = StockDataStream(API_KEY, SECRET_KEY)
    TICKER = TICKER

# Initialize an empty DataFrame to store incoming bar data
columns = ['symbol', 'timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'trade_count', 'vwap']


growing_df = pd.DataFrame(columns=columns)
growing_df_from_alpaca  = pd.DataFrame(columns=columns)


count = 0

# Start trading session
# TODO: Fetch starting balance from alpaca
trading_session = Trading_session(1000)
trade = None

# Async handler to process incoming bar data
async def quote_data_handler(df):
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
        'symbol': df.symbol,
        'timestamp': df.timestamp,
        'Open': df.open,
        'High': df.high,
        'Low': df.low,
        'Close': df.close,
        'Volume': df.volume,
        'trade_count': df.trade_count,
        'vwap': df.vwap
    }

    growing_df_from_alpaca = pd.concat([growing_df_from_alpaca, pd.DataFrame([bar_data])], ignore_index=True)
    copy = growing_df_from_alpaca.copy()

    if(len(copy) > 1): 

        # TODO: Before starting the bot this needs to selected using the generate strategy
        growing_df = combined_strategy(copy, 
                            filter_func=generate_BollingerBands_filter_signal,
                            setup_func=generate_Stochastic_setup_signal,
                            trigger_func=generate_MACD_trigger_signal,
                            filter_params={'bollinger_window': 13, 'num_std_dev': 0.58},
                            setup_params={'k_period': 6, 'd_period': 7, 'stochastic_overbought': 61, 'stochastic_oversold': 44},
                            trigger_params={'fast_period': 3, 'slow_period': 7, 'signal_period': 7})

        print("\nGrowing DataFrame:\n", growing_df.tail(2))
        print("\n")

        trade, trading_session = analyse_latest_alpaca_bar(trading_session, trade, growing_df.iloc[-1], growing_df['timestamp'].iloc[-1])

        count += 1
        


# Subscribe to minute bar updates for SPY
wss_client.subscribe_bars(quote_data_handler, TICKER)


wss_client.run()
