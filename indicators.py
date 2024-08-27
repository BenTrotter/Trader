import pandas as pd

def macd_indicator(df, short_window=12, long_window=26, signal_window=9):
    """
    Calculate the MACD (Moving Average Convergence Divergence) indicator.
    
    Parameters:
    df (pd.DataFrame): DataFrame with 'close' prices.
    short_window (int): The short period for the EMA.
    long_window (int): The long period for the EMA.
    signal_window (int): The period for the MACD signal line.

    Returns:
    pd.DataFrame: DataFrame with MACD and Signal Line.
    """
    df['ema_short'] = df['Close'].ewm(span=short_window, adjust=False).mean()
    df['ema_long'] = df['Close'].ewm(span=long_window, adjust=False).mean()
    df['macd'] = df['ema_short'] - df['ema_long']
    df['signal'] = df['macd'].ewm(span=signal_window, adjust=False).mean()
    
    return df