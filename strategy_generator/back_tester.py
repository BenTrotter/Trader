from alpaca.data.timeframe import TimeFrame
from trading_session import *
from data_visualisation import *
from combined_strategy import *
from indicator_filter import *
from indicator_setup import *
from indicator_trigger import *
from data_fetch import *
from globals import *


def open_trade(open_time, open_price, atr):
    return Trade(
        open_time=open_time,
        open_price_of_trade=open_price,
        open_ATR = atr,
        quantity=QUANTITY)


def calculate_buy_and_hold(df):
    open_price_of_window = df["Open"].iloc[0]
    closing_price_of_window = df["Close"].iloc[-1]
    buy_and_hold = ((closing_price_of_window - open_price_of_window) / open_price_of_window) * 100
    return buy_and_hold


def analyse_row(trading_session, trade, latest_bar):

    if trade is None:
        if latest_bar['Combined_Signal'] == 1:
            trade = open_trade(latest_bar['Datetime'], latest_bar['Close'], latest_bar['ATR']) # Open Long

    elif trade is not None:
        if latest_bar['High'] >= trade.take_profit_price:
            trading_session.add_trade(trade.close_trade(latest_bar['Datetime'], latest_bar['Close'], "Reached take profit")) # Close Long
            trade = None
        elif latest_bar['Combined_Signal'] == -1:
            trading_session.add_trade(trade.close_trade(latest_bar['Datetime'], latest_bar['Close'], "Reached sell signal")) # Close Long
            trade = None
        elif latest_bar['Low'] <= trade.stop_loss_price:
            trading_session.add_trade(trade.close_trade(latest_bar['Datetime'], latest_bar['Close'], "Reached stop loss")) # Close Long
            trade = None

    return trade, trading_session


def backtest_strategy(display_backtester, df):

    buy_and_hold = calculate_buy_and_hold(df)

    trading_session = Trading_session(STARTING_BALANCE)
    trade = None

    for index, row in df.iterrows():
        trade, trading_session = analyse_row(trading_session, trade, row)

    trading_session.calculate_percentage_change_of_strategy()
    trading_session.calculate_average_duration()
    trading_session.calculate_number_of_winning_trades()
    trading_session.calculate_normalized_profit()
    trading_session.calculate_sharpe_ratio()
    
    if display_backtester:
        trading_session.display_trades()
        print(trading_session)
        print(f"Buy and hold: {buy_and_hold}\n")
        plot_strategy(df, "Strategy", trading_session.trades)
    
    return trading_session.get_objectives()


if __name__ == "__main__":
    
    if ALPACA_DATA_SOURCE:
        data = fetch_historic_alpaca_data(TRAINING_PERIOD_START, TRAINING_PERIOD_END, ALPACA_INTERVAL)

    elif YFINANCE_DATA_SOURCE:
        data = fetch_historic_yfinance_data(TRAINING_PERIOD_START, TRAINING_PERIOD_END, YFINANCE_INTERVAL)

    backtest_strategy(True,
                      combined_strategy(data, 
                            filter_func=generate_SMA_filter_signal,
                            setup_func=generate_RSI_setup_signal,
                            trigger_func=generate_MACD_trigger_signal,
                            filter_params={'sma_window': 5, 'look_back_period': 3},
                            setup_params={'period': 14, 'overbought_condition': 60, 'oversold_condition': 40},
                            trigger_params={'fast_period': 12, 'slow_period': 26, 'signal_period': 9}))