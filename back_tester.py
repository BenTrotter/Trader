# backtest_strategy.py
from alpaca.data.timeframe import TimeFrame
from trading_session import *
from data_visualisation import *
from combined_strategy import *
from indicator_filter import *
from indicator_setup import *
from indicator_trigger import *
from data_fetch import *
from globals import *


def open_trade(open_time, open_price, trade_type):
    """
    Args:
        trade_type (boolean): True is long, False is short
    """
    return Trade(
        open_time=open_time,
        open_price=open_price,
        quantity=quantity,
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


def backtest_strategy(display_backtester, data):

    open_price_of_window = data["Open"].iloc[0]
    closing_price_of_window = data["Close"].iloc[-1]
    buy_and_hold = ((closing_price_of_window - open_price_of_window) / open_price_of_window) * 100

    trading_session = Trading_session(starting_balance)

    # Iterate over DataFrame rows and populate list of Trades
    trade = None
    for index, row in data.iterrows():
        trade, trading_session = analyse_row(trading_session, trade, row)

    trading_session.calculate_percentage_change_of_strategy()
    trading_session.calculate_average_duration()
    trading_session.calculate_number_of_winning_trades()
    trading_session.calculate_normalized_profit()
    trading_session.calculate_sharpe_ratio()
    
    if display_backtester:
        trading_session.display_trades()
        print(trading_session)
        print(f"Buy and hold: {buy_and_hold}")
        plot_strategy(data, "Strategy", trading_session.trades)
    
    return trading_session.get_objectives()


if __name__ == "__main__":
    
    if alpaca_data_source:
        data = fetch_historic_alpaca_data(training_period_start, training_period_end, alpaca_interval)

    elif yfinance_data_source:
        data = fetch_historic_yfinance_data(training_period_start, training_period_end, yfinance_interval)

    backtest_strategy(True,
                      combined_strategy(data, 
                            filter_func=generate_SMA_filter_signal,
                            setup_func=generate_RSI_setup_signal,
                            trigger_func=generate_MACD_trigger_signal,
                            filter_params={'sma_window': 5, 'look_back_period': 3},
                            setup_params={'period': 14, 'overbought_condition': 60, 'oversold_condition': 40},
                            trigger_params={'fast_period': 12, 'slow_period': 26, 'signal_period': 9}))