import numpy as np
import pandas as pd


def moving_average_crossover_strategy(data, short_window, long_window):
    """
    Moving average crossover strategy.
    """
    if len(data) < long_window:
        print(f"Not enough data to calculate moving averages. Current data length: {len(data)}")
        return data 
    
    short_window_name = f'SMA_{short_window}'
    long_window_name = f'SMA_{long_window}'
    data[short_window_name] = data['Close'].rolling(window=short_window).mean()
    data[long_window_name] = data['Close'].rolling(window=long_window).mean()
    
    data['Signal'] = 0
    data['Signal'] = np.where((data[short_window_name] > data[long_window_name]) & (data[short_window_name].shift(1) <= data[long_window_name].shift(1)), 1, data['Signal'])
    data['Signal'] = np.where((data[short_window_name] < data[long_window_name]) & (data[short_window_name].shift(1) >= data[long_window_name].shift(1)), -1, data['Signal'])
    
    data.dropna(inplace=True)

    return data


def bollinger_bands_strategy(data, window=20, num_std_dev=2):
    """
    Bollinger Bands strategy.
    """
    data['SMA_20'] = data['Close'].rolling(window=window).mean()
    data['BB_up'] = data['SMA_20'] + num_std_dev * data['Close'].rolling(window=window).std()
    data['BB_dn'] = data['SMA_20'] - num_std_dev * data['Close'].rolling(window=window).std()

    data['Signal'] = 0
    data['Signal'] = np.where(data['Close'] < data['BB_dn'], 1, data['Signal'])
    data['Signal'] = np.where(data['Close'] > data['BB_up'], -1, data['Signal'])

    data['Position'] = data['Signal'].diff()
    data.dropna(inplace=True)

    return data


def macd_crossover_strategy(data):
    """
    MACD crossover strategy.
    """
    data['EMA_12'] = data['Close'].ewm(span=12, adjust=False).mean()
    data['EMA_26'] = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = data['EMA_12'] - data['EMA_26']
    data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()

    data['Signal'] = 0
    data['Signal'] = np.where((data['MACD'] > data['Signal_Line']) & (data['MACD'].shift(1) <= data['Signal_Line'].shift(1)), 1, data['Signal'])
    data['Signal'] = np.where((data['MACD'] < data['Signal_Line']) & (data['MACD'].shift(1) >= data['Signal_Line'].shift(1)), -1, data['Signal'])

    data['Position'] = data['Signal'].diff()
    data.dropna(inplace=True)

    return data


def rsi_strategy(data, window=14, overbought=70, oversold=30):
    """
    RSI strategy.
    """
    delta = data['Close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(window=window, min_periods=1).mean()
    avg_loss = pd.Series(loss).rolling(window=window, min_periods=1).mean()

    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))

    data['Signal'] = 0
    data['Signal'] = np.where(data['RSI'] < oversold, 1, data['Signal'])
    data['Signal'] = np.where(data['RSI'] > overbought, -1, data['Signal'])

    data['Position'] = data['Signal'].diff()
    data.dropna(inplace=True)

    return data


def vwap_strategy(data):
    """
    VWAP strategy.
    """
    data['VWAP'] = (data['Close'] * data['Volume']).cumsum() / data['Volume'].cumsum()

    data['Signal'] = 0
    data['Signal'] = np.where(data['Close'] > data['VWAP'], 1, data['Signal'])
    data['Signal'] = np.where(data['Close'] < data['VWAP'], -1, data['Signal'])

    data['Position'] = data['Signal'].diff()
    data.dropna(inplace=True)

    return data
