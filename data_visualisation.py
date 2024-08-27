import matplotlib.pyplot as plt

def plot_strategy(data, trades, ticker, strategy_name):
    """
    Plots the stock price, signals for buy/sell, and trade points.

    Args:
        data (pd.DataFrame): DataFrame with historical stock data and signals.
        trades (list): List of Trade objects.
        ticker (str): The stock ticker symbol.
        strategy_name (str): The name of the strategy used.
    """
    plt.figure(figsize=(14, 7))

    # Plot the stock's closing price
    plt.plot(data['Close'], label='Close Price', color='blue', alpha=0.5)

    # Plot the moving averages if they exist in the data
    if 'SMA_9' in data.columns:
        plt.plot(data['SMA_9'], label='9-period SMA', color='orange', alpha=0.8)
    if 'SMA_21' in data.columns:
        plt.plot(data['SMA_21'], label='21-period SMA', color='purple', alpha=0.8)

    # Extract trade entry and exit points
    long_open_times = [trade.open_time for trade in trades if trade.long]
    long_open_prices = [trade.open_price for trade in trades if trade.long]
    long_close_times = [trade.close_time for trade in trades if trade.long]
    long_close_prices = [trade.close_price for trade in trades if trade.long]

    short_open_times = [trade.open_time for trade in trades if trade.short]
    short_open_prices = [trade.open_price for trade in trades if trade.short]
    short_close_times = [trade.close_time for trade in trades if trade.short]
    short_close_prices = [trade.close_price for trade in trades if trade.short]

    # Offset for overlapping points, for when we close and open at same time
    offset = 0.005

    # Plot long trades (buy to open, sell to close)
    plt.scatter(long_open_times, long_open_prices, marker='^', color='green', alpha=1, label='Long Open (Buy)', s=100)
    plt.scatter(long_close_times, [price + offset for price in long_close_prices], marker='v', color='red', alpha=1, label='Long Close (Sell)', s=100)

    # Plot short trades (sell to open, buy to close)
    plt.scatter(short_open_times, short_open_prices, marker='v', color='purple', alpha=1, label='Short Open (Sell)', s=100)
    plt.scatter(short_close_times, [price - offset for price in short_close_prices], marker='^', color='orange', alpha=1, label='Short Close (Buy)', s=100)

    # Customize the plot
    plt.title(f'Backtesting {ticker} Strategy: {strategy_name}')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()

    # Show the plot
    plt.show()