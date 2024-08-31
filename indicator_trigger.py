import numpy as np
from data_fetch import *


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
    ticker = "AMZN"
    period_start = '2024-08-28'
    period_end = '2024-08-29'
    interval = '5m'
    df = fetch_historic_yfinance_data(ticker, period_start, period_end, interval)
    print(generate_MACD_trigger_signal(df, 10, 5))


if __name__ == "__main__":
    test_indicator()