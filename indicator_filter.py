import pandas as pd
from data_fetch import *
from globals import *

def generate_SMA_filter_signal(df, sma_window, look_back_period):
    """
    Filter signal which checks that the previous 3 closing prices have been above the SMA with period defined as sma_window
    """
    sma_window_name = f'SMA_{sma_window}'
    df[sma_window_name] = df['Close'].rolling(window=sma_window).mean()

    # Initialize the 'signal' column with NaN
    df['Filter_Signal'] = 0

    # Loop through the DataFrame starting from the 3rd row
    for i in range(3, len(df)):
        # Check if the previous three closing prices are greater than the SMA
        if all(df.loc[i-look_back_period:i-1, 'Close'] > df.loc[i-look_back_period:i-1, sma_window_name]):
            df.loc[i, 'Filter_Signal'] = 1  # Buy signal
        elif all(df.loc[i-look_back_period:i-1, 'Close'] < df.loc[i-look_back_period:i-1, sma_window_name]):
            df.loc[i, 'Filter_Signal'] = -1  # Sell signal
    
    return df


def test_indicator():
    df = fetch_historic_yfinance_data(training_period_start, training_period_end, yfinance_interval)
    print(generate_SMA_filter_signal(df, 10, 5))


if __name__ == "__main__":
    test_indicator()