import os
from globals import *
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import *
from alpaca.trading.enums import OrderSide, TimeInForce
from dotenv import load_dotenv
from trading_session import *
from back_tester import open_trade


load_dotenv(override=True)

# Initialize the WebSocket client
if(CRYPTO):
    time_in_force = TimeInForce.GTC
    TICKER = CRYPTO_TICKER
elif(STOCK):
    time_in_force = TimeInForce.DAY
    TICKER = TICKER

# Alpaca API credentials
API_KEY = os.getenv('ALPACA_PERSONAL_API_KEY_ID')
SECRET_KEY = os.getenv('ALPACA_PERSONAL_API_SECRET_KEY')


trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)


# TODO: we need to get the stop loss / take profit working
def prepare_open_long_order(ticker, quantity, take_profit_price, stop_loss_price):
    take_profit = TakeProfitRequest(limit_price=take_profit_price)
    stop_loss = StopLossRequest(stop_price=stop_loss_price)
    return MarketOrderRequest(
                        symbol=ticker,
                        qty=quantity,
                        side=OrderSide.BUY,
                        time_in_force=time_in_force,
                        take_profit= take_profit,
                        stop_loss=stop_loss)



def open_trade_alpaca(trade):
    print("Opening a long position")
    order = prepare_open_long_order(TICKER, QUANTITY, trade.take_profit_price, trade.stop_loss_price)
    trading_client.submit_order(order_data=order)
    return trade


def close_trade_alpaca():
    print("Closing all trades")
    trading_client.close_all_positions()


def analyse_latest_alpaca_bar(trading_session, trade, latest_bar):

    if trade is None:
        if latest_bar['Combined_Signal'] == 1:
            trade = open_trade(latest_bar['Datetime'], latest_bar['Close'], latest_bar['ATR']) # Open Long
            open_trade_alpaca(trade) # Open Long

    elif trade is not None:
        if latest_bar['High'] >= trade.take_profit_price:
            trading_session.add_trade(trade.close_trade(latest_bar['Datetime'], latest_bar['Close'], "Reached take profit")) # Close Long
            trade = None
        elif latest_bar['Combined_Signal'] == -1:
            trading_session.add_trade(trade.close_trade(latest_bar['Datetime'], latest_bar['Close'], "Reached sell signal")) # Close Long
            close_trade_alpaca()
            trade = None
        elif latest_bar['Low'] <= trade.stop_loss_price:
            trading_session.add_trade(trade.close_trade(latest_bar['Datetime'], latest_bar['Close'], "Reached stop loss")) # Close Long
            trade = None


    return trade, trading_session