# backtest_strategy.py
import pandas as pd
import yfinance as yf
import os
from trading_session import *
from datetime import datetime
from strategies import *
from data_visualisation import *

def fetch_historical_data(ticker, period, interval):
    """
    Fetches historical stock data for a given ticker.
    Args:
        ticker (str): The stock ticker symbol.
    Returns:
        pd.DataFrame: DataFrame with historical stock data.
    """
    return yf.download(ticker, period=period, interval=interval)


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


def analyse_row(trading_session, trade, row, index):
    if trade != None:
        if trade.long:
            if row['High'] >= trade.take_profit_price:
                trading_session.add_trade(trade.close_trade(index, row['Close'], "Reached take profit")) # Close Long
                trade = None
            elif row['Signal'] == -1:
                trading_session.add_trade(trade.close_trade(index, row['Close'], "Next short signal reached")) # Close Long
                trade = open_trade(index, row['Close'], False) # Open short
            elif row['Low'] <= trade.stop_loss_price:
                trading_session.add_trade(trade.close_trade(index, row['Close'], "Reached stop loss")) # Close Long
                trade = None
        
        elif trade.short:
            if row['Low'] <= trade.take_profit_price:
                trading_session.add_trade(trade.close_trade(index, row['Close'], "Reached take profit")) # Close Short
                trade = None
            elif row['Signal'] == 1:
                trading_session.add_trade(trade.close_trade(index, row['Close'], "Next long signal reached")) # Close Short
                trade = open_trade(index, row['Close'], True) # Open Long
            elif row['High'] >= trade.stop_loss_price:
                trading_session.add_trade(trade.close_trade(index, row['Close'], "Reached stop loss")) # Close Short
                trade = None

    elif trade == None:
        if row['Signal'] == 1:
            trade = open_trade(index, row['Close'], True)
        elif row['Signal'] == -1:
            trade = open_trade(index, row['Close'], False)

    return trade, trading_session

def backtest_strategy(ticker, period, interval, strategy, *args):

    data = fetch_historical_data(ticker, period, interval)
    strategy_data = strategy(data, *args)
    strategy_data.to_csv(os.path.abspath(os.getcwd())+'/'+ticker+'.csv')
    print(strategy_data)
    
    trading_session = Trading_session(1000)

    # Convert the Datetime column to datetime objects
    strategy_data.index = pd.to_datetime(strategy_data.index)

    # Iterate over DataFrame rows and populate list of Trades
    trade = None
    for index, row in strategy_data.iterrows():
        trade, trading_session = analyse_row(trading_session, trade, row, index)
        
    trading_session.display_trades()
    trading_session.calculate_percentage_change_of_strategy()
    trading_session.calculate_average_duration()
    plot_strategy(strategy_data, trading_session.trades, ticker, "MA Crossover")
    print(trading_session)

    return trading_session.percentage_change_of_strategy
    

if __name__ == "__main__":
    ticker = 'AMZN'
    backtest_strategy(ticker, "1d", "1m", moving_average_crossover_strategy, 9, 21)
