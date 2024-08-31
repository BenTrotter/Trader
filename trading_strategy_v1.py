import numpy as np
import pandas as pd
from back_tester import fetch_historical_data
import os

FILTER = []
SET_UP = []
TRIGGER = []

# Stragey with filter, setup and trigger
def SMA_RSI_MACD_Strat(df, 
                       sma_window,
                       look_back_period, 
                       period, 
                       overbought_condition, 
                       oversold_condition,
                       fast_period, 
                       slow_period, 
                       signal_period):
    
    generate_SMA_filter_signal(df, sma_window, look_back_period)
    generate_RSI_setup_signal(df, period, overbought_condition, oversold_condition)
    generate_MACD_trigger_signal(df, fast_period, slow_period, signal_period)

    df.dropna(inplace=True)

    # Assuming your DataFrame is named df
    df['Combined_Signal'] = df[['Filter_Signal', 'Setup_Signal', 'Trigger_Signal']].apply(
        lambda row: 1 if all(row == 1) else (-1 if all(row == -1) else 0),
        axis=1
    )

    return df

# Filter signal which checks that the previous 3 closing prices have been above the SMA with period defined as sma_window
def generate_SMA_filter_signal(df, sma_window, look_back_period):

    df.reset_index(inplace=True)

    sma_window_name = f'SMA_{sma_window}'

    df[sma_window_name] = df['Close'].rolling(window=sma_window).mean()

    # Initialize the 'signal' column with NaN
    df['Filter_Signal'] = np.nan

    # Loop through the DataFrame starting from the 3rd row
    for i in range(3, len(df)):
        # Check if the previous three closing prices are greater than the SMA
        if all(df.loc[i-look_back_period:i-1, 'Close'] > df.loc[i-look_back_period:i-1, sma_window_name]):
            df.loc[i, 'Filter_Signal'] = 1  # Buy signal
        elif all(df.loc[i-look_back_period:i-1, 'Close'] < df.loc[i-look_back_period:i-1, sma_window_name]):
            df.loc[i, 'Filter_Signal'] = -1  # Sell signal
    
    return df

# Set up signal
def generate_RSI_setup_signal(df, period, overbought_condition, oversold_condition):
    
    # Step 1: Calculate Price Changes
    df['Delta'] = df['Close'].diff()

    # Step 2: Calculate Gains and Losses
    df['Gain'] = df['Delta'].where(df['Delta'] > 0, 0)
    df['Loss'] = -df['Delta'].where(df['Delta'] < 0, 0)

    # Step 3: Calculate the Average Gain and Loss
    df['avg_gain'] = df['Gain'].rolling(window=period).mean()
    df['avg_loss'] = df['Loss'].rolling(window=period).mean()

    # Step 4: Calculate the Relative Strength (RS)
    df['rs'] = df['avg_gain'] / df['avg_loss']

    # Step 5: Calculate the RSI
    df['rsi'] = 100 - (100 / (1 + df['rs']))

    # Define the conditions for buy, sell, and hold signals
    conditions = [
        (df['rsi'] > overbought_condition),   # Overbought - Sell Signal
        (df['rsi'] < oversold_condition),   # Oversold - Buy Signal
        ((df['rsi'] <= overbought_condition) & (df['rsi'] >= oversold_condition))  # Neutral - Hold Signal
    ]

    # Define corresponding signal values
    signals = [1, -1, 0]

    # Create a new column 'signal' in the DataFrame
    df['Setup_Signal'] = np.select(conditions, signals)

    return df

# Trigger signal
def generate_MACD_trigger_signal(df, fast_period, slow_period, signal_period):

    # Step 1: Calculate the fast and slow EMAs
    df['EMA_fast'] = df['Close'].ewm(span=fast_period, min_periods=fast_period, adjust=False).mean()
    df['EMA_slow'] = df['Close'].ewm(span=slow_period, min_periods=slow_period, adjust=False).mean()

    # Step 2: Calculate the MACD line
    df['MACD_line'] = df['EMA_fast'] - df['EMA_slow']

    # Step 3: Calculate the Signal line
    df['Signal_line'] = df['MACD_line'].ewm(span=signal_period, adjust=False).mean()

    # Step 4: Generate MACD signals
    # Positive MACD cross occurs when the MACD line crosses above the Signal line (buy signal)
    # Negative MACD cross occurs when the MACD line crosses below the Signal line (sell signal)
    df['Trigger_Signal'] = np.where(df['MACD_line'] > df['Signal_line'], 1, 0)  # 1 for a positive cross, 0 otherwise

    # Step 5: Detect actual cross
    df['Trigger_Signal'] = df['Trigger_Signal'].diff()  # Difference to detect the crossing

    # Step 6: Set the signal values
    # 1 for a positive cross (buy signal)
    # -1 for a negative cross (sell signal)
    df['Trigger_Signal'] = df['Trigger_Signal'].apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))

    return df


def test_indicator():
    df = fetch_historical_data("AAPL", "1d", "1m")
    # print(generate_sma_signal(df, 60))
    # print(generate_RSI_signal(df, 14, 70, 30).head(10))
    print(generate_MACD_trigger_signal(df, 6, 12, 5).head(10))

def test_strategy():
    ticker="AAPL"
    data_period = "5d"
    data_interval = "1m"
    df = fetch_historical_data(ticker, data_period, data_interval)
    df = (SMA_RSI_MACD_Strat(df, 
                            60,
                            3,
                            14,
                            70,
                            30,
                            6, 
                            12, 
                            5))
    signal_columns = ['Datetime', 'Filter_Signal', 'Setup_Signal', 'Trigger_Signal', 'Combined_Signal', 'Close']
    print(df[signal_columns])
    df[signal_columns].to_csv(os.path.abspath(os.getcwd())+'/'+ticker+'.csv')


if __name__ == "__main__":
    test_strategy()