import os
import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from dotenv import load_dotenv

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
    bars_df = data_client.get_crypto_bars(request_params).df if crypto else data_client.get_stock_bars(request_params).df

    # Reset the index to add a sequential index column and turn the current index columns into regular columns
    bars_df.reset_index(inplace=True)

    bars_df.columns = ['Symbol', 'Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Trade_Count', 'VWAP']

    print(bars_df)
    print(len(bars_df))

if __name__ == "__main__":
    fetch_historic_alpaca_data(True, False, "2023-01-01", "2024-01-01", "AAPL", TimeFrame.Day)
