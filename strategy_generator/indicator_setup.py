import numpy as np
from data_fetch import *


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


def generate_Stochastic_setup_signal(df, k_period, d_period, stochastic_overbought, stochastic_oversold):
    """
    Stochastic Oscillator setup that identifies overbought/oversold conditions.
    
    df: DataFrame containing the trading data.
    k_period: Number of periods for %K line.
    d_period: Number of periods for %D line (smoothed %K).
    overbought: Threshold above which the asset is considered overbought.
    oversold: Threshold below which the asset is considered oversold.
    
    Returns: DataFrame with the 'Setup_Signal' column added.
    """
    df['L14'] = df['Low'].rolling(window=k_period).min()
    df['H14'] = df['High'].rolling(window=k_period).max()
    df['%K'] = 100 * ((df['Close'] - df['L14']) / (df['H14'] - df['L14']))
    df['%D'] = df['%K'].rolling(window=d_period).mean()

    df['Setup_Signal'] = 0  # Initialize with neutral

    df.loc[df['%D'] > stochastic_overbought, 'Setup_Signal'] = -1  # Sell signal
    df.loc[df['%D'] < stochastic_oversold, 'Setup_Signal'] = 1    # Buy signal
    
    return df


def generate_ADX_setup_signal(df, adx_window, strong_trend_threshold):
    """
    ADX (Average Directional Index) Setup Signal to identify strong uptrends.
    
    df: DataFrame containing the trading data.
    adx_window: Number of periods to calculate the ADX.
    strong_trend_threshold: The ADX value above which the trend is considered strong.
    
    Returns: DataFrame with the original columns, 'Setup_Signal', and 'ADX'.
    """
    # Step 1: Calculate True Range (TR)
    df['High-Low'] = df['High'] - df['Low']
    df['High-Close'] = abs(df['High'] - df['Close'].shift(1))
    df['Low-Close'] = abs(df['Low'] - df['Close'].shift(1))
    
    # True Range is the maximum of these
    df['TR'] = df[['High-Low', 'High-Close', 'Low-Close']].max(axis=1)
    
    # Step 2: Calculate Directional Movement (+DM and -DM)
    df['+DM'] = np.where((df['High'] - df['High'].shift(1)) > (df['Low'].shift(1) - df['Low']), 
                         np.maximum((df['High'] - df['High'].shift(1)), 0), 0)
    df['-DM'] = np.where((df['Low'].shift(1) - df['Low']) > (df['High'] - df['High'].shift(1)), 
                         np.maximum((df['Low'].shift(1) - df['Low']), 0), 0)
    
    # Step 3: Smooth the True Range and Directional Movements
    df['ATR'] = df['TR'].rolling(window=adx_window).mean()
    df['+DI'] = (df['+DM'].rolling(window=adx_window).mean() / df['ATR']) * 100
    df['-DI'] = (df['-DM'].rolling(window=adx_window).mean() / df['ATR']) * 100
    
    # Step 4: Calculate the Directional Index (DX) and ADX
    df['DX'] = (abs(df['+DI'] - df['-DI']) / (df['+DI'] + df['-DI'])) * 100
    df['ADX'] = df['DX'].rolling(window=adx_window).mean()
    
    # Step 5: Setup signal based on ADX and +DI > -DI (indicating a strong uptrend)
    df['Setup_Signal'] = np.where((df['ADX'] > strong_trend_threshold) & (df['+DI'] > df['-DI']), 1, 0)  # Buy signal for strong uptrend
    
    # Drop all columns except original columns, 'Setup_Signal', and 'ADX'
    df = df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Setup_Signal', 'ADX']]

    return df


def test_indicator():
    df = fetch_data("Training")
    # Test the ADX setup signal method
    adx_window = 14  # Common period for ADX calculation
    strong_trend_threshold = 30  # ADX > 25 indicates a strong trend
    print(generate_ADX_setup_signal(df, adx_window, strong_trend_threshold))
    
    # print(df_with_adx_signal[['ADX', 'Setup_Signal']])


if __name__ == "__main__":
    test_indicator()