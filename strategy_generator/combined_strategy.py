import os
from globals import *
from data_fetch import *
from indicator_filter import *
from indicator_setup import *
from indicator_trigger import *


def combined_strategy(df, filter_func, setup_func, trigger_func, filter_params={}, setup_params={}, trigger_params={}):

    df = calculate_atr(df)

    # Apply filter, setup, and trigger functions to the DataFrame
    df = filter_func(df, **filter_params)
    df = setup_func(df, **setup_params)
    df = trigger_func(df, **trigger_params)

    # Combine the signals into a final trading signal
    df['Combined_Signal'] = df[['Filter_Signal', 'Setup_Signal', 'Trigger_Signal']].apply(
        lambda row: 1 if all(val == 1 for val in row if val != 9) else 
                    (-1 if all(val == -1 for val in row if val != 9) else 0),
        axis=1
    )

    return df



def calculate_atr(df):
    """
    Calculate the Average True Range (ATR) for a given DataFrame.

    Args:
        df (pd.DataFrame): DataFrame with 'High', 'Low', and 'Close' columns.

    Returns:
        pd.DataFrame: The input DataFrame with an additional 'ATR' column.
    """
    # Calculate True Range (TR)
    high_low = df['High'] - df['Low']
    high_close = abs(df['High'] - df['Close'].shift(1))
    low_close = abs(df['Low'] - df['Close'].shift(1))
    
    # Combine to get the True Range - take the maximum of the three possible values
    df['TR'] = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    
    # Calculate the ATR
    df['ATR'] = df['TR'].rolling(window=ATR_PERIOD, min_periods=1).mean()
    
    # Drop the intermediate 'TR' column
    df.drop(columns=['TR'], inplace=True)

    return df


if __name__ == "__main__":
    df = fetch_data("Training")
    df = (combined_strategy(df, 
                            filter_func=generate_SMA_filter_signal,
                            setup_func=generate_RSI_setup_signal,
                            trigger_func=generate_MACD_trigger_signal,
                            filter_params={'sma_window': 50, 'look_back_period': 3},
                            setup_params={'period': 14, 'overbought_condition': 70, 'oversold_condition': 30},
                            trigger_params={'fast_period': 12, 'slow_period': 26, 'signal_period': 9}))
    signal_columns = ['Datetime', 'Filter_Signal', 'Setup_Signal', 'Trigger_Signal', 'Combined_Signal', 'Close']
    print(df[signal_columns])
    df[signal_columns].to_csv(os.path.abspath(os.getcwd())+'/'+TICKER+'.csv')