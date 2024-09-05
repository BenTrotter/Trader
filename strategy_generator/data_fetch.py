import os
from dotenv import load_dotenv
from globals import *
from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest
import pandas as pd
import yfinance as yf



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
    df = yf.download(TICKER, start=start_date, end=end_date, interval=interval)

    df.reset_index(inplace=True)
    
    # Check for 'Date' or 'Datetime' column and handle accordingly
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df.rename(columns={'Date': 'Datetime'}, inplace=True)
    elif 'Datetime' in df.columns:
        df['Datetime'] = pd.to_datetime(df['Datetime'])

    df = calculate_atr(df)
    
    return df


def fetch_historic_alpaca_data(period_start, period_end, interval):

    # Load environment variables from .env file
    load_dotenv(override=True)

    ALPACA_PERSONAL_API_KEY_ID = os.getenv('ALPACA_PERSONAL_API_KEY_ID')
    ALPACA_PERSONAL_API_SECRET_KEY = os.getenv('ALPACA_PERSONAL_API_SECRET_KEY')

    period_start = pd.to_datetime(period_start)
    period_end = pd.to_datetime(period_end)
    
    if STOCK:
        data_client = StockHistoricalDataClient(ALPACA_PERSONAL_API_KEY_ID, ALPACA_PERSONAL_API_SECRET_KEY)
        request_params = StockBarsRequest(
            symbol_or_symbols=TICKER,
            timeframe=interval,
            start=period_start,
            end=period_end
        )
    elif CRYPTO:
        data_client = CryptoHistoricalDataClient(ALPACA_PERSONAL_API_KEY_ID, ALPACA_PERSONAL_API_SECRET_KEY)
        request_params = CryptoBarsRequest(
            symbol_or_symbols=CRYPTO_TICKER,
            timeframe=interval,
            start=period_start,
            end=period_end
        )
    else:
        raise ValueError("Specify either stock or crypto as True.")

    df = data_client.get_crypto_bars(request_params).df if CRYPTO else data_client.get_stock_bars(request_params).df

    # Reset the index to add a sequential index column and turn the current index columns into regular columns
    df.reset_index(inplace=True)

    df.columns = ['Symbol', 'Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Trade_Count', 'VWAP']

    df = calculate_atr(df)

    return df
 

def calculate_atr(df):
    """
    Calculate the Average True Range (ATR) for a given DataFrame.

    Args:
        df (pd.DataFrame): DataFrame with 'High', 'Low', and 'Close' columns.

    Returns:
        pd.DataFrame: The input DataFrame with an additional 'ATR' column.
    """
    # Calculate True Range (TR)
    high_low = df['High'] - df['Low']
    high_close = abs(df['High'] - df['Close'].shift(1))
    low_close = abs(df['Low'] - df['Close'].shift(1))
    
    # Combine to get the True Range - take the maximum of the three possible values
    df['TR'] = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    
    # Calculate the ATR
    df['ATR'] = df['TR'].rolling(window=ATR_PERIOD, min_periods=1).mean()
    
    # Drop the intermediate 'TR' column
    df.drop(columns=['TR'], inplace=True)

    return df


def fetch_data(data_window_type):

    if ALPACA_DATA_SOURCE:

        if data_window_type == 'Training':
            df = fetch_historic_alpaca_data(TRAINING_PERIOD_START, TRAINING_PERIOD_END, ALPACA_INTERVAL)

        elif data_window_type == 'Unseen':
            df = fetch_historic_alpaca_data(UNSEEN_PERIOD_START, UNSEEN_PERIOD_END, ALPACA_INTERVAL)

    elif YFINANCE_DATA_SOURCE:

        if data_window_type == 'Training': 
            df = fetch_historic_yfinance_data(TRAINING_PERIOD_START, TRAINING_PERIOD_END, YFINANCE_INTERVAL)

        elif data_window_type == 'Unseen':
            df = fetch_historic_yfinance_data(UNSEEN_PERIOD_START, UNSEEN_PERIOD_END, YFINANCE_INTERVAL)

    return df


if __name__ == "__main__":
    df = fetch_data('Unseen')
    print(df)