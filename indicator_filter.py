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


def generate_BollingerBands_filter_signal(df, bollinger_window, num_std_dev):
    """
    Bollinger Bands filter that identifies potential buy/sell zones.
    
    df: DataFrame containing the trading data.
    window: Number of periods for moving average and standard deviation.
    num_std_dev: Number of standard deviations to set the upper and lower bands.
    
    Returns: DataFrame with the 'Filter_Signal' column added.
    """
    df['MA'] = df['Close'].rolling(window=bollinger_window).mean()
    df['BB_Upper'] = df['MA'] + num_std_dev * df['Close'].rolling(window=bollinger_window).std()
    df['BB_Lower'] = df['MA'] - num_std_dev * df['Close'].rolling(window=bollinger_window).std()

    df['Filter_Signal'] = 0  # Initialize with neutral

    df.loc[df['Close'] > df['BB_Upper'], 'Filter_Signal'] = -1  # Sell signal when price is above upper band
    df.loc[df['Close'] < df['BB_Lower'], 'Filter_Signal'] = 1   # Buy signal when price is below lower band
    
    return df


def test_indicator():
    df = fetch_historic_yfinance_data(training_period_start, training_period_end, yfinance_interval)
    print(generate_BollingerBands_filter_signal(df, 10, 0.5))


if __name__ == "__main__":
    test_indicator()