import matplotlib.pyplot as plt

def plot_strategy(data, ticker, strategy_name):
    """
    Plots the stock price, signals for buy/sell, and trade points.

    Args:
        data (pd.DataFrame): DataFrame with historical stock data and signals.
        ticker (str): The stock ticker symbol.
        strategy_name (str): The name of the strategy used.
    """
    plt.figure(figsize=(14, 7))

    # Plot the stock's closing price
    plt.plot(data['Close'], label='Close Price', color='blue', alpha=0.5)

    # Identify buy and sell signals
    buy_signals = data[data['Combined_Signal'] == 1]
    sell_signals = data[data['Combined_Signal'] == -1]

    # Plot buy signals
    plt.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='green', alpha=1, label='Buy Signal', s=100)

    # Plot sell signals
    plt.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='red', alpha=1, label='Sell Signal', s=100)

    # Customize the plot
    plt.title(f'Backtesting {ticker} Strategy: {strategy_name}')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()

    # Show the plot
    plt.show()
