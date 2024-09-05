from alpaca.data.live import StockDataStream, CryptoDataStream
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from alpaca_functions import *
from trading_session import *
from indicator_filter import *
from indicator_setup import *
from indicator_trigger import *
from combined_strategy import combined_strategy
from datetime import timezone 
from globals import *


# Count back should be another for all indicators in strategy to be able to calculate signals
def prepopulate_df(count_back):
    period_end = datetime.now(timezone.utc) 
    period_start = period_end - (count_back * pd.Timedelta(ALPACA_INTERVAL.value))
    df = fetch_historic_alpaca_data(period_start, period_end, ALPACA_INTERVAL)
    return df


# TODO: Before starting the bot this needs to selected using the generate strategy
def strategy(df):
    return combined_strategy(df, 
                            filter_func=generate_BollingerBands_filter_signal,
                            setup_func=generate_Stochastic_setup_signal,
                            trigger_func=generate_MACD_trigger_signal,
                            filter_params={'bollinger_window': 13, 'num_std_dev': 0.58},
                            setup_params={'k_period': 6, 'd_period': 7, 'stochastic_overbought': 61, 'stochastic_oversold': 44},
                            trigger_params={'fast_period': 3, 'slow_period': 7, 'signal_period': 7})



load_dotenv(override=True)

API_KEY = os.getenv('ALPACA_PERSONAL_API_KEY_ID')
SECRET_KEY = os.getenv('ALPACA_PERSONAL_API_SECRET_KEY')

# Initialize the WebSocket client
if(CRYPTO):
    wss_client = CryptoDataStream(API_KEY, SECRET_KEY)
    TICKER = CRYPTO_TICKER
elif(STOCK):
    wss_client = StockDataStream(API_KEY, SECRET_KEY)
    TICKER = TICKER

columns = ['Symbol', 'Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Trade_Count', 'VWAP']
growing_alpaca_df  = pd.DataFrame(columns=columns)
growing_alpaca_df = prepopulate_df(100)
growing_strategy_df = strategy(growing_alpaca_df.copy())

count = 0

# TODO: Fetch starting balance from alpaca
trading_session = Trading_session(1000)
trade = None

# Async handler to process incoming bar data
async def quote_data_handler(df):
    global growing_alpaca_df 
    global growing_strategy_df
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
        'Symbol': df.symbol,
        'Datetime': df.timestamp,
        'Open': df.open,
        'High': df.high,
        'Low': df.low,
        'Close': df.close,
        'Volume': df.volume,
        'Trade_Count': df.trade_count,
        'VWAP': df.vwap
    }

    growing_alpaca_df = pd.concat([growing_alpaca_df, pd.DataFrame([bar_data])], ignore_index=True)
    copy = growing_alpaca_df.copy()

    if(len(copy) > 1): 

        growing_strategy_df = strategy(copy)

        print("\nGrowing strategy DataFrame:\n", growing_strategy_df[['Symbol', 'Datetime', 'Close', 'Filter_Signal', 'Setup_Signal', 'Trigger_Signal', 'Combined_Signal']].tail(5))
        print("\n")
        # print("\nGrowing Alpacs DataFrame:\n", growing_alpaca_df)
        # print("\n")

        trade, trading_session = analyse_latest_alpaca_bar(trading_session, trade, growing_strategy_df.iloc[-1])

        count += 1
        

# Subscribe to minute bar updates for SPY
wss_client.subscribe_bars(quote_data_handler, TICKER)

wss_client.run()


