from globals import *
import pandas as pd
from data_fetch import *


def noop_filter(df):
    """
    No-operation filter that assigns a constant value of 9 to the 'Filter_Signal' column.
    """
    # Initialize the 'Filter_Signal' column with the value 9
    df['Filter_Signal'] = 9
    return df


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

def generate_ATR_filter_signal(df, filter_atr_window, atr_upper_threshold, atr_lower_threshold):
    # Calculate True Range (TR)
    high_low = df['High'] - df['Low']
    high_close = abs(df['High'] - df['Close'].shift(1))
    low_close = abs(df['Low'] - df['Close'].shift(1))
    
    # Combine to get the True Range - take the maximum of the three possible values
    df['Filter_TR'] = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    
    # Calculate the ATR
    df['Filter_ATR'] = df['Filter_TR'].rolling(window=filter_atr_window, min_periods=1).mean()
    
    # Initialize 'Filter_Signal' with neutral (0)
    df['Filter_Signal'] = 0

    # Generate a buy signal if ATR is above the threshold (high volatility) and sell if it's below (low volatility)
    df.loc[df['Filter_ATR'] > atr_upper_threshold, 'Filter_Signal'] = 1  # Buy signal for high volatility
    df.loc[df['Filter_ATR'] < atr_lower_threshold, 'Filter_Signal'] = -1  # Sell signal for low volatility

    # Drop the intermediate 'TR' column
    df.drop(columns=['Filter_TR'], inplace = True)
    df.drop(columns=['Filter_ATR'], inplace = True)

    return df


def test_indicator():
    df = fetch_data("Training")
    print(generate_ATR_filter_signal(df, 14, 28, 15))  # ATR window of 14 with upper threshold 0.05 and lower threshold 0.02


if __name__ == "__main__":
    test_indicator()