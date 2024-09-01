# backtest_strategy.py
from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest
import pandas as pd
import yfinance as yf
import os
from dotenv import load_dotenv
from globals import *


def fetch_historic_yfinance_data(start_date, end_date, interval):
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
    
    # Check for 'Date' or 'Datetime' column and handle accordingly
    if 'Date' in download_df.columns:
        download_df['Date'] = pd.to_datetime(download_df['Date'])
        download_df.rename(columns={'Date': 'Datetime'}, inplace=True)
    elif 'Datetime' in download_df.columns:
        download_df['Datetime'] = pd.to_datetime(download_df['Datetime'])
    
    return download_df


def fetch_historic_alpaca_data(period_start, period_end, interval):

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
            symbol_or_symbols=ticker,
            timeframe=interval,
            start=period_start,
            end=period_end
        )
    elif crypto:
        data_client = CryptoHistoricalDataClient(ALPACA_PERSONAL_API_KEY_ID, ALPACA_PERSONAL_API_SECRET_KEY)
        request_params = CryptoBarsRequest(
            symbol_or_symbols=crypto_ticker,
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


def fetch_data(data_window_type):

    if alpaca_data_source:

        if data_window_type == 'Training':
            data = fetch_historic_alpaca_data(training_period_start, training_period_end, alpaca_interval)

        elif data_window_type == 'Unseen':
            data = fetch_historic_alpaca_data(unseen_period_start, unseen_period_start, alpaca_interval)

    elif yfinance_data_source:

        if data_window_type == 'Training': 
            data = fetch_historic_yfinance_data(training_period_start, training_period_end, yfinance_interval)

        elif data_window_type == 'Unseen':
            data = fetch_historic_yfinance_data(unseen_period_start, unseen_period_end, yfinance_interval)

    return data