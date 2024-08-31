# backtest_strategy.py
import pandas as pd
import yfinance as yf
import os
from trading_session import *
from datetime import datetime
from strategies import *
from data_visualisation import *
from  trading_strategy_v1 import SMA_RSI_MACD_Strat


def fetch_historical_data(ticker, period, interval):
    """
    Fetches historical stock data for a given ticker.
    Args:
        ticker (str): The stock ticker symbol.
    Returns:
        pd.DataFrame: DataFrame with historical stock data.
    """
    download_df = yf.download(ticker, period=period, interval=interval)
    download_df.reset_index(inplace=True)
    return download_df


def open_trade(open_time, open_price, trade_type):
    """
    Args:
        trade_type (boolean): True is long, False is short
    """
    return Trade(
        open_time=open_time,
        open_price=open_price,
        quantity=1,
        long=trade_type,
        short= not trade_type,
        take_profit_pct=0.04,
        stop_loss_pct=0.02)


def analyse_row(trading_session, trade, row):
    if trade != None:
        if trade.long:
            # if row['High'] >= trade.take_profit_price:
            #     trading_session.add_trade(trade.close_trade(index, row['Close'], "Reached take profit")) # Close Long
            #     trade = None
            if row['Combined_Signal'] == -1:
                trading_session.add_trade(trade.close_trade(row['Datetime'], row['Close'], "Next short signal reached")) # Close Long
                trade = None
            # elif row['Low'] <= trade.stop_loss_price:
            #     trading_session.add_trade(trade.close_trade(index, row['Close'], "Reached stop loss")) # Close Long
            #     trade = None

    elif trade == None:
        if row['Combined_Signal'] == 1:
            trade = open_trade(row['Datetime'], row['Close'], True) # Open Long

    return trade, trading_session


def backtest_strategy(data):

    trading_session = Trading_session(1000)

    # Convert the Datetime column to datetime objects
    data['Datetime'] = pd.to_datetime(data['Datetime'])

    # Iterate over DataFrame rows and populate list of Trades
    trade = None
    for index, row in data.iterrows():
        trade, trading_session = analyse_row(trading_session, trade, row)
        
    trading_session.display_trades()
    trading_session.calculate_percentage_change_of_strategy()
    trading_session.calculate_average_duration()
    plot_strategy(data, ticker, "Strategy", trading_session.trades)
    print(trading_session)

    return trading_session.percentage_change_of_strategy
    

if __name__ == "__main__":
    ticker = 'AMZN'
    data_period = "5d"
    data_interval = "1m"
    data = fetch_historical_data(ticker, data_period, data_interval)
    backtest_strategy(SMA_RSI_MACD_Strat(data, 60,3, 14, 70,30, 6, 12, 5))
