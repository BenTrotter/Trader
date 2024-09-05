from globals import *
import matplotlib.pyplot as plt
import pandas as pd


def plot_strategy(df, strategy_name, trades):
    """
    Plots the stock price, signals for buy/sell, and trade points.

    Args:
        data (pd.DataFrame): DataFrame with historical stock data and signals.
        ticker (str): The stock ticker symbol.
        strategy_name (str): The name of the strategy used.
        trades (list): A list of Trade objects containing the trades to plot.
    """
    # Ensure the "Datetime" column is in datetime format
    if not pd.api.types.is_datetime64_any_dtype(df['Datetime']):
        df['Datetime'] = pd.to_datetime(df['Datetime'])

    # Set the "Datetime" column as the DataFrame's index
    df.set_index('Datetime', inplace=True)

    plt.figure(figsize=(14, 7))

    # Plot the stock's closing price
    plt.plot(df['Close'], label='Close Price', color='blue', alpha=0.5)

    # Prepare lists for trade open and close points
    open_times = []
    open_prices = []
    close_times = []
    close_prices = []

    # Collect trade data for plotting outside the loop
    for trade in trades:
        # Ensure trade times are in datetime format
        if not isinstance(trade.open_time, pd.Timestamp):
            trade.open_time = pd.to_datetime(trade.open_time)
        if not isinstance(trade.close_time, pd.Timestamp):
            trade.close_time = pd.to_datetime(trade.close_time)

        # Append trade data to the respective lists
        open_times.append(trade.open_time)
        open_prices.append(trade.open_price)
        close_times.append(trade.close_time)
        close_prices.append(trade.close_price)

    # Plot all trade open points at once
    plt.scatter(open_times, open_prices, marker='^', color='green', alpha=1, label='Trade Open', s=100)

    # Plot all trade close points at once
    plt.scatter(close_times, close_prices, marker='v', color='red', alpha=1, label='Trade Close', s=100)

    # Customize the plot
    plt.title(f'Backtesting {TICKER} Strategy: {strategy_name}')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend(loc='best')
    plt.grid()

    # Format x-axis dates
    plt.gcf().autofmt_xdate()

    # Show the plot
    plt.show()