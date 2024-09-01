import numpy as np
from data_fetch import *
from globals import *


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


def generate_MA_crossover_trigger_signal(df, short_window, long_window):
    """
    Moving Average Crossover trigger that identifies potential buy/sell signals.
    
    df: DataFrame containing the trading data.
    short_window: Number of periods for the short-term moving average.
    long_window: Number of periods for the long-term moving average.
    
    Returns: DataFrame with the 'Trigger_Signal' column added.
    """
    df['MA_Short'] = df['Close'].rolling(window=short_window).mean()
    df['MA_Long'] = df['Close'].rolling(window=long_window).mean()

    df['Trigger_Signal'] = 0  # Initialize with neutral

    # Buy signal when short-term MA crosses above long-term MA
    df.loc[(df['MA_Short'] > df['MA_Long']) & (df['MA_Short'].shift(1) <= df['MA_Long'].shift(1)), 'Trigger_Signal'] = 1
    
    # Sell signal when short-term MA crosses below long-term MA
    df.loc[(df['MA_Short'] < df['MA_Long']) & (df['MA_Short'].shift(1) >= df['MA_Long'].shift(1)), 'Trigger_Signal'] = -1
    
    return df


def test_indicator():
    df = fetch_historic_yfinance_data(training_period_start, training_period_end, yfinance_interval)
    print(generate_MA_crossover_trigger_signal(df, 5, 20))


if __name__ == "__main__":
    test_indicator()