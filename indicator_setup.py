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


def test_indicator():
    df = fetch_historic_yfinance_data(training_period_start, training_period_end, yfinance_interval)
    print(generate_Stochastic_setup_signal(df, k_period=14, d_period=3, stochastic_overbought=60, stochastic_oversold=40))


if __name__ == "__main__":
    test_indicator()