# backtest_strategy.py
from alpaca.data.timeframe import TimeFrame
from trading_session import *
from data_visualisation import *
from trading_strategies import *
from indicator_filter import *
from indicator_setup import *
from indicator_trigger import *
from data_fetch import *


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


def backtest_strategy(ticker, display_backtester, data):

    trading_session = Trading_session(1000)

    # Iterate over DataFrame rows and populate list of Trades
    trade = None
    for index, row in data.iterrows():
        trade, trading_session = analyse_row(trading_session, trade, row)

    trading_session.calculate_percentage_change_of_strategy()
    trading_session.calculate_average_duration()
    
    if display_backtester:
        trading_session.display_trades()
        print(trading_session)
        plot_strategy(data, ticker, "Strategy", trading_session.trades)
    
    return trading_session.percentage_change_of_strategy
    

if __name__ == "__main__":
    
    data_source = 'YFinance'
    ticker = "AMZN"
    period_start = '2024-08-28'
    period_end = '2024-08-29'

    if data_source == 'Alpaca':

        # Fetch alpaca data arguments
        stock = True
        crypto = False
        time_frame = TimeFrame.Minute

        data = fetch_historic_alpaca_data(stock, crypto, period_start, period_end, ticker, time_frame)

    elif data_source == 'YFinance':
        interval = '5m'
        data = fetch_historic_yfinance_data(ticker, period_start, period_end, interval)

    backtest_strategy(ticker,
                      True,
                      combined_strategy(data, 
                            filter_func=generate_SMA_filter_signal,
                            setup_func=generate_RSI_setup_signal,
                            trigger_func=generate_MACD_trigger_signal,
                            filter_params={'sma_window': 50, 'look_back_period': 3},
                            setup_params={'period': 14, 'overbought_condition': 70, 'oversold_condition': 30},
                            trigger_params={'fast_period': 12, 'slow_period': 26, 'signal_period': 9}))