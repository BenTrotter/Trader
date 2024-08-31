import os
from indicator_filter import *
from indicator_setup import *
from indicator_trigger import *
from data_fetch import *


def combined_strategy(df, filter_func, setup_func, trigger_func, filter_params={}, setup_params={}, trigger_params={}):
    # Apply filter, setup, and trigger functions to the DataFrame
    df = filter_func(df, **filter_params)
    df = setup_func(df, **setup_params)
    df = trigger_func(df, **trigger_params)

    # Combine the signals into a final trading signal
    df['Combined_Signal'] = df[['Filter_Signal', 'Setup_Signal', 'Trigger_Signal']].apply(
        lambda row: 1 if all(row == 1) else (-1 if all(row == -1) else 0),
        axis=1
    )

    return df


if __name__ == "__main__":
    ticker="AAPL"
    data_period = "5d"
    data_interval = "1m"
    df = fetch_historic_yfinance_data(ticker, data_period, data_interval)
    df = (combined_strategy(df, 
                            filter_func=generate_SMA_filter_signal,
                            setup_func=generate_RSI_setup_signal,
                            trigger_func=generate_MACD_trigger_signal,
                            filter_params={'sma_window': 50, 'look_back_period': 3},
                            setup_params={'period': 14, 'overbought_condition': 70, 'oversold_condition': 30},
                            trigger_params={'fast_period': 12, 'slow_period': 26, 'signal_period': 9}))
    signal_columns = ['Datetime', 'Filter_Signal', 'Setup_Signal', 'Trigger_Signal', 'Combined_Signal', 'Close']
    print(df[signal_columns])
    df[signal_columns].to_csv(os.path.abspath(os.getcwd())+'/'+ticker+'.csv')








# # Stragey with filter, setup and trigger
# def SMA_RSI_MACD_Strat(df, 
#                        sma_window,
#                        look_back_period, 
#                        period, 
#                        overbought_condition, 
#                        oversold_condition,
#                        fast_period, 
#                        slow_period, 
#                        signal_period):
    
#     generate_SMA_filter_signal(df, sma_window, look_back_period)
#     generate_RSI_setup_signal(df, period, overbought_condition, oversold_condition)
#     generate_MACD_trigger_signal(df, fast_period, slow_period, signal_period)

#     df.dropna(inplace=True)

#     # Assuming your DataFrame is named df
#     df['Combined_Signal'] = df[['Filter_Signal', 'Setup_Signal', 'Trigger_Signal']].apply(
#         lambda row: 1 if all(row == 1) else (-1 if all(row == -1) else 0),
#         axis=1
#     )

#     return df    