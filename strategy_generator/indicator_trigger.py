from globals import *
import numpy as np
from data_fetch import *


def noop_trigger(df):
    """
    No-operation trigger that assigns a constant value of 9 to the 'Trigger_Signal' column.
    """
    # Initialize the 'Filter_Signal' column with the value 9
    df['Trigger_Signal'] = 9
    return df


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


def generate_parabolic_sar_trigger_signal(df, initial_af=0.02, max_af=0.2, step_af=0.02):
    """
    Parabolic SAR trigger that identifies potential buy/sell signals.
    
    df: DataFrame containing the trading data.
    initial_af: The initial acceleration factor (default: 0.02).
    max_af: The maximum acceleration factor (default: 0.2).
    step_af: The step increment for the acceleration factor (default: 0.02).
    
    Returns: DataFrame with the 'Trigger_Signal' column added.
    """
    
    # Initialize necessary columns
    df['SAR'] = df['Close'].iloc[0]  # Starting SAR
    df['EP'] = df['High'].iloc[0] if df['Close'].iloc[0] < df['Close'].iloc[1] else df['Low'].iloc[0]  # Extreme Price (EP)
    df['AF'] = initial_af  # Start with the initial acceleration factor (AF)
    df['Trend'] = 1 if df['Close'].iloc[1] > df['Close'].iloc[0] else -1  # Initial trend direction

    for i in range(2, len(df)):
        prior_sar = df['SAR'].iloc[i - 1]
        prior_ep = df['EP'].iloc[i - 1]
        prior_af = df['AF'].iloc[i - 1]
        prior_trend = df['Trend'].iloc[i - 1]
        
        # Calculate the new SAR
        if prior_trend == 1:  # Uptrend
            sar = prior_sar + prior_af * (prior_ep - prior_sar)
            sar = min(sar, df['Low'].iloc[i - 1], df['Low'].iloc[i])  # Ensure SAR stays below current lows
            new_ep = max(prior_ep, df['High'].iloc[i])  # Update EP (highest high)
            
            if df['Close'].iloc[i] < sar:  # Trend reversal
                df.loc[i, 'SAR'] = prior_ep  # Reset SAR to prior EP
                df.loc[i, 'Trend'] = -1  # Switch to downtrend
                df.loc[i, 'AF'] = initial_af  # Reset AF
                df.loc[i, 'EP'] = df['Low'].iloc[i]  # Set new EP (lowest low)
            else:
                df.loc[i, 'SAR'] = sar
                df.loc[i, 'Trend'] = 1  # Continue uptrend
                df.loc[i, 'AF'] = min(prior_af + step_af, max_af)  # Increase AF up to max
                df.loc[i, 'EP'] = new_ep
        
        else:  # Downtrend
            sar = prior_sar + prior_af * (prior_ep - prior_sar)
            sar = max(sar, df['High'].iloc[i - 1], df['High'].iloc[i])  # Ensure SAR stays above current highs
            new_ep = min(prior_ep, df['Low'].iloc[i])  # Update EP (lowest low)
            
            if df['Close'].iloc[i] > sar:  # Trend reversal
                df.loc[i, 'SAR'] = prior_ep  # Reset SAR to prior EP
                df.loc[i, 'Trend'] = 1  # Switch to uptrend
                df.loc[i, 'AF'] = initial_af  # Reset AF
                df.loc[i, 'EP'] = df['High'].iloc[i]  # Set new EP (highest high)
            else:
                df.loc[i, 'SAR'] = sar
                df.loc[i, 'Trend'] = -1  # Continue downtrend
                df.loc[i, 'AF'] = min(prior_af + step_af, max_af)  # Increase AF up to max
                df.loc[i, 'EP'] = new_ep
    
    # Generate Parabolic SAR trigger signals
    df['Trigger_Signal'] = np.where((df['Close'] > df['SAR']) & (df['Trend'] == 1), 1, 0)  # Buy signal when price crosses above SAR
    df['Trigger_Signal'] = np.where((df['Close'] < df['SAR']) & (df['Trend'] == -1), -1, df['Trigger_Signal'])  # Sell signal when price crosses below SAR
    
    return df


def test_indicator():
    df = fetch_data("Training")
    print(generate_parabolic_sar_trigger_signal(df))
    

if __name__ == "__main__":
    test_indicator()