# backtest_strategy.py
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

def fetch_historical_data(ticker):
    """
    Fetches historical stock data for a given ticker.
    Args:
        ticker (str): The stock ticker symbol.
    Returns:
        pd.DataFrame: DataFrame with historical stock data.
    """
    return yf.download(ticker, period='1mo', interval='5m')

def moving_average_crossover_strategy(data, stop_loss_pct=0.02, take_profit_pct=0.05):
    """
    Simple moving average crossover strategy with stop-loss and take-profit.
    Args:
        data (pd.DataFrame): Historical stock data.
        stop_loss_pct (float): Stop-loss percentage.
        take_profit_pct (float): Take-profit percentage.
    Returns:
        pd.DataFrame: DataFrame with buy/sell signals, stop-loss, and take-profit levels.
    """
    # Calculate moving averages
    data['SMA_9'] = data['Close'].rolling(window=9).mean()
    data['SMA_21'] = data['Close'].rolling(window=21).mean()
    
    # Initialize Signal, Position, Stop_Loss, and Take_Profit columns
    data['Signal'] = 0
    data['Position'] = 0
    data['Stop_Loss'] = np.nan
    data['Take_Profit'] = np.nan
    
    # Generate signals
    data['Signal'] = np.where(data['SMA_9'] > data['SMA_21'], 1, -1)
    data['Position'] = data['Signal'].diff()
    
    # Use .loc to update Stop_Loss and Take_Profit
    for i in range(1, len(data)):
        if data['Signal'].iloc[i] == 1:
            data.loc[data.index[i], 'Stop_Loss'] = data['Close'].iloc[i] * (1 - stop_loss_pct)
            data.loc[data.index[i], 'Take_Profit'] = data['Close'].iloc[i] * (1 + take_profit_pct)
        elif data['Signal'].iloc[i] == -1:
            data.loc[data.index[i], 'Stop_Loss'] = data['Close'].iloc[i] * (1 + stop_loss_pct)
            data.loc[data.index[i], 'Take_Profit'] = data['Close'].iloc[i] * (1 - take_profit_pct)
    
    # Clean up NaN values
    data.dropna(inplace=True)
    
    return data



def vwap_bollinger_rsi_strategy(data):
    """
    Strategy using VWAP, Bollinger Bands, and RSI.
    Args:
        data (pd.DataFrame): Historical stock data.
    Returns:
        pd.DataFrame: DataFrame with buy/sell signals.
    """
    # Calculate VWAP
    data['VWAP'] = (data['Close'] * data['Volume']).cumsum() / data['Volume'].cumsum()

    # Calculate Bollinger Bands
    data['SMA_14'] = data['Close'].rolling(window=14).mean()
    data['BB_Upper'] = data['SMA_14'] + 2 * data['Close'].rolling(window=14).std()
    data['BB_Lower'] = data['SMA_14'] - 2 * data['Close'].rolling(window=14).std()
    
    # Calculate RSI
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))

    # Initialize Signal and Position columns
    data['Signal'] = 0
    data['Position'] = 0

    # Generate signals based on the combination of VWAP, Bollinger Bands, and RSI
    for i in range(15, len(data)):
        # Buy condition: Above VWAP, RSI < 45, and Close below previous lower Bollinger Band
        if (data['Close'].iloc[i] > data['VWAP'].iloc[i - 15:i].mean() and 
            data['RSI'].iloc[i] < 45 and 
            data['Close'].iloc[i] < data['BB_Lower'].iloc[i-1]):
            data.at[data.index[i], 'Signal'] = 1  # Buy signal

        # Sell condition: Below VWAP, RSI > 55, and Close above previous upper Bollinger Band
        elif (data['Close'].iloc[i] < data['VWAP'].iloc[i - 15:i].mean() and 
              data['RSI'].iloc[i] > 55 and 
              data['Close'].iloc[i] > data['BB_Upper'].iloc[i-1]):
            data.at[data.index[i], 'Signal'] = -1  # Sell signal

    # Determine positions
    data['Position'] = data['Signal'].diff()

    # Clean up NaN values created by rolling calculations
    data.dropna(inplace=True)
    
    return data

def plot_strategy(data, ticker, strategy_name):
    """
    Plots the stock price and signals for buy/sell.
    Args:
        data (pd.DataFrame): DataFrame with historical stock data and signals.
        ticker (str): The stock ticker symbol.
        strategy_name (str): The name of the strategy used.
    """
    plt.figure(figsize=(14,7))
    plt.plot(data['Close'], label='Close Price', color='blue', alpha=0.5)
    
    if 'SMA_9' in data.columns:
        plt.plot(data['SMA_9'], label='9-period SMA', color='orange', alpha=0.8)
    if 'SMA_21' in data.columns:
        plt.plot(data['SMA_21'], label='21-period SMA', color='purple', alpha=0.8)
    if 'VWAP' in data.columns:
        plt.plot(data['VWAP'], label='VWAP', color='cyan', alpha=0.8)
    if 'BB_Upper' in data.columns and 'BB_Lower' in data.columns:
        plt.plot(data['BB_Upper'], label='Bollinger Upper', color='red', linestyle='--', alpha=0.7)
        plt.plot(data['BB_Lower'], label='Bollinger Lower', color='green', linestyle='--', alpha=0.7)

    # Plot buy signals
    plt.plot(data.loc[data['Position'] == 2].index, 
             data['Close'][data['Position'] == 2],
             '^', markersize=10, color='g', lw=0, label='Buy Signal')

    # Plot sell signals
    plt.plot(data.loc[data['Position'] == -2].index, 
             data['Close'][data['Position'] == -2],
             'v', markersize=10, color='r', lw=0, label='Sell Signal')
    
    plt.title(f'Backtesting {ticker} Strategy: {strategy_name}')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    plt.show()

def calculate_performance(data):
    """
    Calculates basic performance metrics for the strategy.
    Args:
        data (pd.DataFrame): DataFrame with historical stock data and signals.
    """
    # Calculate returns
    data['Returns'] = data['Close'].pct_change()
    data['Strategy_Returns'] = data['Returns'] * data['Signal'].shift(1)
    
    # Calculate cumulative returns
    cumulative_returns = (data['Strategy_Returns'] + 1).cumprod() - 1
    total_return = cumulative_returns.iloc[-1]
    
    # Performance metrics
    num_trades = data['Position'].abs().sum()
    num_wins = len(data[(data['Position'] == 2) & (data['Returns'] > 0)]) + len(data[(data['Position'] == -2) & (data['Returns'] < 0)])
    win_rate = num_wins / num_trades if num_trades > 0 else 0
    
    print(f"Total Return: {total_return * 100:.2f}%")
    print(f"Number of Trades: {num_trades}")
    print(f"Win Rate: {win_rate * 100:.2f}%")

def backtest_strategy(ticker, strategy):
    """
    Backtests the trading strategy on historical data.
    Args:
        ticker (str): The stock ticker symbol to test.
        strategy (str): The strategy to use ('moving_average' or 'vwap_bollinger_rsi').
    """
    # Fetch data
    data = fetch_historical_data(ticker)
    
    # Apply selected strategy
    if strategy == 'moving_average':
        strategy_data = moving_average_crossover_strategy(data)
        strategy_name = "Moving Average Crossover"
    elif strategy == 'vwap_bollinger_rsi':
        strategy_data = vwap_bollinger_rsi_strategy(data)
        strategy_name = "VWAP + Bollinger Bands + RSI"
    else:
        print("Invalid strategy selected.")
        return
    
    # Plot strategy
    plot_strategy(strategy_data, ticker, strategy_name)
    
    # Calculate and display performance
    calculate_performance(strategy_data)

if __name__ == "__main__":
    ticker = 'AAPL'
    
    # Choose the strategy to backtest
    # strategy = 'vwap_bollinger_rsi'  # Options: 'moving_average' or 'vwap_bollinger_rsi'
    strategy = 'moving_average'
    backtest_strategy(ticker, strategy)
