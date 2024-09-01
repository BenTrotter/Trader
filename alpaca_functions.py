from alpaca.trading.client import TradingClient
from alpaca.trading.requests import *
from alpaca.trading.enums import OrderSide, TimeInForce
import os
from dotenv import load_dotenv
from trading_session import *
from globals import *

# Load environment variables from .env file
load_dotenv(override=True)

# Initialize the WebSocket client
if(crypto):
    time_in_force = TimeInForce.GTC
    ticker = crypto_ticker
elif(stock):
    time_in_force = TimeInForce.DAY
    ticker = ticker

# Alpaca API credentials
API_KEY = os.getenv('ALPACA_API_KEY')
SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')


# paper=True enables paper trading
trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)


def prepare_open_long_order(ticker, quantity, take_profit_price, stop_loss_price):
    take_profit = TakeProfitRequest(limit_price=take_profit_price)
    stop_loss = StopLossRequest(stop_price=stop_loss_price)
    return MarketOrderRequest(
                        symbol=ticker,
                        qty=quantity,
                        side=OrderSide.BUY,
                        time_in_force=time_in_force,
                        take_profit= take_profit,
                        stop_loss=stop_loss
                        )

def prepare_open_short_order(ticker, quantity, take_profit_price, stop_loss_price):
    take_profit = TakeProfitRequest(limit_price=take_profit_price)
    stop_loss = StopLossRequest(stop_price=stop_loss_price)
    return MarketOrderRequest(
                        symbol=ticker,
                        qty=quantity,
                        side=OrderSide.SELL,
                        time_in_force=time_in_force,
                        take_profit= take_profit,
                        stop_loss=stop_loss
                        )


def prepare_close_long_order():
    trading_client.close_position()
    return ClosePositionRequest(

    )

def send_order(order):
    trading_client.submit_order(order_data=order)


def open_trade(open_time, open_price, trade_type):
    """
    Args:
        trade_type (boolean): True is long, False is short
    """
    trade = Trade(
        open_time=open_time,
        open_price=open_price,
        quantity=quantity,
        long=trade_type,
        short= not trade_type,
        take_profit_pct=0.04,
        stop_loss_pct=0.02)

    if(trade_type):
        print("Opening a long position")
        order = prepare_open_long_order(ticker, quantity, trade.take_profit_price, trade.stop_loss_price)
    else:
        print("Opening a short position")
        order = prepare_open_short_order(ticker, quantity, trade.take_profit_price, trade.stop_loss_price)

    send_order(order)

    return trade

def close_trade_alpaca():
    print("Closing all trades")
    trading_client.close_all_positions()


def analyse_latest_alpaca_bar(trading_session, trade, row, index):
    if trade != None:
        if trade.long:
            if row['High'] >= trade.take_profit_price:
                trading_session.add_trade(trade.close_trade(index, row['Close'], "Reached take profit")) # Close Long
                # close_trade_alpaca()
                trade = None
            elif row['Signal'] == -1:
                trading_session.add_trade(trade.close_trade(index, row['Close'], "Next short signal reached")) # Close Long
                close_trade_alpaca()
                trade = None
                # trade = open_trade(index, row['Close'], False) # Open short
            elif row['Low'] <= trade.stop_loss_price:
                trading_session.add_trade(trade.close_trade(index, row['Close'], "Reached stop loss")) # Close Long
                # close_trade_alpaca()
                trade = None

    elif trade == None:
        if row['Signal'] == 1:
            trade = open_trade(index, row['Close'], True) # Open Long

    return trade, trading_session