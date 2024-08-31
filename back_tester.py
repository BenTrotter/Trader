# backtest_strategy.py
import pandas as pd
import yfinance as yf
import os
from trading_session import *
from datetime import datetime
from data_visualisation import *
from  trading_strategies import *
from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from dotenv import load_dotenv


def fetch_historic_yfinance_data(ticker, start_date, end_date, interval):
    """
    Fetches historical stock data for a given ticker between two dates.
    Args:
        ticker (str): The stock ticker symbol.
        start_date (str): The start date for data retrieval (format 'YYYY-MM-DD').
        end_date (str): The end date for data retrieval (format 'YYYY-MM-DD').
        interval (str): The data interval (e.g., '1d', '1m', '5m').
    Returns:
        pd.DataFrame: DataFrame with historical stock data.
    """

    # Fetch data between start_date and end_date
    download_df = yf.download(ticker, start=start_date, end=end_date, interval=interval)

    download_df.reset_index(inplace=True)

    # Convert the Datetime column to datetime objects
    download_df['Datetime'] = pd.to_datetime(download_df['Datetime'])

    return download_df


def fetch_historic_alpaca_data(stock, crypto, period_start, period_end, symbol_symbols, interval):

    # Load environment variables from .env file
    load_dotenv(override=True)

    # Alpaca API credentials
    ALPACA_PERSONAL_API_KEY_ID = os.getenv('ALPACA_PERSONAL_API_KEY_ID')
    ALPACA_PERSONAL_API_SECRET_KEY = os.getenv('ALPACA_PERSONAL_API_SECRET_KEY')

    # Common code for both stock and crypto
    period_start = pd.to_datetime(period_start)
    period_end = pd.to_datetime(period_end)
    
    # Choose the client and request parameters based on the type of asset
    if stock:
        data_client = StockHistoricalDataClient(ALPACA_PERSONAL_API_KEY_ID, ALPACA_PERSONAL_API_SECRET_KEY)
        request_params = StockBarsRequest(
            symbol_or_symbols=[symbol_symbols],
            timeframe=interval,
            start=period_start,
            end=period_end
        )
    elif crypto:
        data_client = CryptoHistoricalDataClient(ALPACA_PERSONAL_API_KEY_ID, ALPACA_PERSONAL_API_SECRET_KEY)
        request_params = CryptoBarsRequest(
            symbol_or_symbols=[symbol_symbols],
            timeframe=interval,
            start=period_start,
            end=period_end
        )
    else:
        raise ValueError("Specify either stock or crypto as True.")

    # Fetch the data
    download_data = data_client.get_crypto_bars(request_params).df if crypto else data_client.get_stock_bars(request_params).df

    # Reset the index to add a sequential index column and turn the current index columns into regular columns
    download_data.reset_index(inplace=True)

    download_data.columns = ['Symbol', 'Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Trade_Count', 'VWAP']

    return download_data


def open_trade(open_time, open_price, trade_type):
    """
    Args:
        trade_type (boolean): True is long, False is short
    """
    return Trade(
        open_time=open_time,
        open_price=open_price,
        quantity=1,
        long=trade_type,
        short= not trade_type,
        take_profit_pct=0.04,
        stop_loss_pct=0.02)


def analyse_row(trading_session, trade, row):
    if trade != None:
        if trade.long:
            # if row['High'] >= trade.take_profit_price:
            #     trading_session.add_trade(trade.close_trade(index, row['Close'], "Reached take profit")) # Close Long
            #     trade = None
            if row['Combined_Signal'] == -1:
                trading_session.add_trade(trade.close_trade(row['Datetime'], row['Close'], "Next short signal reached")) # Close Long
                trade = None
            # elif row['Low'] <= trade.stop_loss_price:
            #     trading_session.add_trade(trade.close_trade(index, row['Close'], "Reached stop loss")) # Close Long
            #     trade = None

    elif trade == None:
        if row['Combined_Signal'] == 1:
            trade = open_trade(row['Datetime'], row['Close'], True) # Open Long

    return trade, trading_session


def backtest_strategy(ticker, display_backtester, data):

    trading_session = Trading_session(1000)

    # Iterate over DataFrame rows and populate list of Trades
    trade = None
    for index, row in data.iterrows():
        trade, trading_session = analyse_row(trading_session, trade, row)

    trading_session.calculate_percentage_change_of_strategy()
    trading_session.calculate_average_duration()
    
    if display_backtester:
        trading_session.display_trades()
        print(trading_session)
        plot_strategy(data, ticker, "Strategy", trading_session.trades)
    
    return trading_session.percentage_change_of_strategy
    

if __name__ == "__main__":
    
    data_source = 'YFinance'
    ticker = "AMZN"
    period_start = '2024-08-28'
    period_end = '2024-08-29'

    if data_source == 'Alpaca':

        # Fetch alpaca data arguments
        stock = True
        crypto = False
        time_frame = TimeFrame.Minute

        data = fetch_historic_alpaca_data(stock, crypto, period_start, period_end, ticker, time_frame)

    elif data_source == 'YFinance':
        interval = '5m'
        data = fetch_historic_yfinance_data(ticker, period_start, period_end, interval)

    backtest_strategy(ticker,
                      True,
                      combined_strategy(data, 
                            filter_func=generate_SMA_filter_signal,
                            setup_func=generate_RSI_setup_signal,
                            trigger_func=generate_MACD_trigger_signal,
                            filter_params={'sma_window': 50, 'look_back_period': 3},
                            setup_params={'period': 14, 'overbought_condition': 70, 'oversold_condition': 30},
                            trigger_params={'fast_period': 12, 'slow_period': 26, 'signal_period': 9}))