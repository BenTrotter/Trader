# backtest_strategy.py
import pandas as pd
import yfinance as yf
import os
from trade import Trade
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



def calculate_average_duration(trades):
    # Check if the trades list is empty
    if not trades:
        return "00:00:00"  # or return None, or raise an exception as per your needs

    # Calculate total duration in seconds
    total_seconds = sum(trade.calculate_duration_in_seconds() for trade in trades)
    
    # Calculate average duration in seconds
    average_seconds = total_seconds / len(trades)
    
    # Convert average duration to HH:MM:SS format
    hours = int(average_seconds // 3600)
    minutes = int((average_seconds % 3600) // 60)
    seconds = int(average_seconds % 60)
    
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def open_trade(open_time, open_price, trade_type):
    """
    Args:
        trade_type (boolean): True is long, False is short
    """
    return Trade(
        open_time=open_time,
        open_price=open_price,
        quantity=1000,
        long=trade_type,
        short= not trade_type,
        take_profit_pct=0.04,
        stop_loss_pct=0.02
        )


def display_trades(trades):
    total_profit = 0
    for tr in trades:
        total_profit = tr.profit + total_profit
        print(tr)
    
    print(f"\nTotal profit: ${total_profit:.2f}")
    print(f"Number of trades: {len(trades)}")
    print(f"Average duration of trade: {calculate_average_duration(trades)}\n\n")


# TODO: We need to enhance this method
def calculate_performance_of_trades(trades):
    total_profit_pct = 0
    for tr in trades:
        total_profit_pct = tr.profit_pct + total_profit_pct
    print(f"\nTotal profit percentage for strategy: {total_profit_pct}\n")
    return total_profit_pct


def backtest_strategy(ticker):

    data = fetch_historical_data(ticker, "1d", "1m")
    strategy_data = moving_average_crossover_strategy(data)
    strategy_data.to_csv(os.path.abspath(os.getcwd())+'/'+ticker+'.csv')
    trades = []

    # Convert the Datetime column to datetime objects
    strategy_data.index = pd.to_datetime(strategy_data.index)

    # Iterate over DataFrame rows and populate list of Trades
    trade = None
    for index, row in strategy_data.iterrows():

        if trade != None:
            if trade.long:
                if row['High'] >= trade.take_profit_price:
                    trades.append(trade.close_trade(index, row['Close'], "Reached take profit")) # Close Long
                    trade = None
                elif row['Signal'] == -1:
                    trades.append(trade.close_trade(index, row['Close'], "Next short signal reached")) # Close Long
                    trade = open_trade(index, row['Close'], False) # Open short
                elif row['Low'] <= trade.stop_loss_price:
                    trades.append(trade.close_trade(index, row['Close'], "Reached stop loss")) # Close Long
                    trade = None
            
            elif trade.short:
                if row['Low'] <= trade.take_profit_price:
                    trades.append(trade.close_trade(index, row['Close'], "Reached take profit")) # Close Short
                    trade = None
                elif row['Signal'] == 1:
                    trades.append(trade.close_trade(index, row['Close'], "Next long signal reached")) # Close Short
                    trade = open_trade(index, row['Close'], True) # Open Long
                elif row['High'] >= trade.stop_loss_price:
                    trades.append(trade.close_trade(index, row['Close'], "Reached stop loss")) # Close Short
                    trade = None

        elif trade == None:
            if row['Signal'] == 1:
                trade = open_trade(index, row['Close'], True)
            elif row['Signal'] == -1:
                trade = open_trade(index, row['Close'], False)
        
    display_trades(trades)
    plot_strategy(strategy_data,trades, ticker, "MA Crossover")

    return calculate_performance_of_trades(trades)
    

if __name__ == "__main__":
    ticker = 'AMZN'
    backtest_strategy(ticker)
