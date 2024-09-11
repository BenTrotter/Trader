import os
import sys
from dotenv import load_dotenv
import pandas as pd
from alpaca.data.live import StockDataStream, CryptoDataStream
from alpaca_functions import *
from trading_session import *
from data_visualisation import *
from indicator_filter import *
from indicator_setup import *
from indicator_trigger import *
from combined_strategy import combined_strategy
from datetime import timezone 
from globals import *
import signal

shutdown_flag = False

def prepopulate_df(count_back):
    period_end = datetime.now(timezone.utc) -  (15 * pd.Timedelta(ALPACA_INTERVAL.value))
    period_start = period_end - (count_back * pd.Timedelta(ALPACA_INTERVAL.value))
    df = fetch_historic_alpaca_data(period_start, period_end, ALPACA_INTERVAL)
    return df

# TODO: THIS IS WHERE WE WILL DEFINE THE STRATEGY FOR THE BOT
def strategy(df):
    return combined_strategy(df,
                             filter_func=noop_filter,
                             setup_func=generate_Stochastic_setup_signal,
                             trigger_func=noop_trigger,
                             filter_params={},
                             setup_params={'k_period': 6, 'd_period': 3, 'stochastic_overbought': 67, 'stochastic_oversold': 30},
                             trigger_params={})

def handle_shutdown_signal(signal_number, frame):
    global shutdown_flag
    print(f"\n\nReceived signal {signal_number}. Shutting down gracefully...")
    shutdown_flag = True

load_dotenv(override=True)
API_KEY = os.getenv('ALPACA_PERSONAL_API_KEY_ID')
SECRET_KEY = os.getenv('ALPACA_PERSONAL_API_SECRET_KEY')

# Initialize the WebSocket client
if CRYPTO:
    wss_client = CryptoDataStream(API_KEY, SECRET_KEY)
    TICKER = CRYPTO_TICKER
elif STOCK:
    wss_client = StockDataStream(API_KEY, SECRET_KEY)
    TICKER = TICKER

columns = ['Symbol', 'Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Trade_Count', 'VWAP']
growing_alpaca_df = pd.DataFrame(columns=columns)
growing_alpaca_df = prepopulate_df(100)
growing_strategy_df = strategy(growing_alpaca_df.copy())

trading_session = Trading_session(get_current_buying_power())
trade = None

# Async handler to process incoming bar data
async def quote_data_handler(df):
    global growing_alpaca_df
    global growing_strategy_df
    global trading_session
    global trade

    if shutdown_flag:
        print("Shutdown flag is set. Exiting the quote data handler.")
        print(f"\n\n ****** Displaying trading session ****** \n\n")
        trading_session.display_trades()
        trading_session.calculate_percentage_change_of_strategy()
        trading_session.calculate_normalized_profit()
        trading_session.calculate_number_of_winning_trades()
        trading_session.calculate_average_duration()
        trading_session.calculate_sharpe_ratio_v2
        print(trading_session)
        plot_strategy(growing_strategy_df, "Strategy", trading_session.trades)
        print(f"\n\nRemember to check Alpaca trading dashboard for any remaining open trades and handle appropriately\n\n")
        sys.exit(0)
        return

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

    if len(copy) > 1:
        growing_strategy_df = strategy(copy)
        print("\nGrowing strategy DataFrame:\n", growing_strategy_df[['Symbol', 'Datetime', 'Low', 'High', 'Close', 'Filter_Signal', 'Setup_Signal', 'Trigger_Signal', 'Combined_Signal']].tail(1))
        trade, trading_session = analyse_latest_alpaca_bar(trading_session, trade, growing_strategy_df.iloc[-1])


def run_ws_client():
    try:
        wss_client.subscribe_bars(quote_data_handler, TICKER)
        wss_client.run()
    except Exception as e:
        print(f"Error running WebSocket client: {e}")
    finally:
        print("WebSocket client terminated.")

# Register the signal handler for clean shutdown
signal.signal(signal.SIGINT, handle_shutdown_signal)
signal.signal(signal.SIGTERM, handle_shutdown_signal)


if __name__ == "__main__":
    run_ws_client()