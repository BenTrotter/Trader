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


def test_indicator():
    df = fetch_historic_yfinance_data(training_period_start, training_period_end, yfinance_interval)
    print(generate_RSI_setup_signal(df, 10, 5))


if __name__ == "__main__":
    test_indicator()