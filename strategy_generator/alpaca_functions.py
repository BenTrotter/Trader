import os
from globals import *
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import *
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.common.exceptions import APIError 
from dotenv import load_dotenv
from trading_session import *
from back_tester import open_trade
import logging

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


# Setting up logging configuration (optional)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_trade_info(take_profit_price, stop_loss_price, order_response):

    logging.info("----------------------------------------")
    logging.info("Opened a long position:")
    logging.info(f"Ticker: {TICKER}")
    logging.info(f"Quantity: {QUANTITY}")

    if take_profit_price != 0.0:
        logging.info(f"Take Profit Price: ${take_profit_price:.2f}")
        logging.info(f"Stop Loss Price: ${stop_loss_price:.2f}")

    try:
        order_details = trading_client.get_order_by_id(str(order_response.id))
        logging.info(f"Order ID: {order_details.id}")
        logging.info(f"Order Status: {order_details.status}")

        if order_details.filled_avg_price:
            logging.info(f"Bought at: ${float(order_details.filled_avg_price):.2f}")
        else:
            logging.info("Order not filled yet.")
    except Exception as e:
        logging.error(f"Error retrieving order status: {e}")

    logging.info("----------------------------------------\n\n")


# ********* OPENING TRADES ********** #

def prepare_and_submit_bracket_order(take_profit_price, stop_loss_price):
    take_profit = TakeProfitRequest(limit_price=take_profit_price)
    stop_loss = StopLossRequest(stop_price=stop_loss_price)
    try:
        # Submit a bracket order (market buy + attached take-profit and stop-loss)
        market_order = MarketOrderRequest(
            symbol=TICKER,
            qty=QUANTITY,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY,
            order_class="bracket",
            take_profit=take_profit,
            stop_loss=stop_loss
        )
        order_response = trading_client.submit_order(order_data=market_order)

    except APIError as api_err:
        print(f"Alpaca API error: {api_err}")
        return None
    except Exception as e:
        print(f"An unexpected error occured: {e}")
        return None
    
    return order_response


def prepare_and_submit_open_long_order():
    try:
        market_order = MarketOrderRequest(
                            symbol=TICKER,
                            qty=QUANTITY,
                            side=OrderSide.BUY,
                            time_in_force=time_in_force)
        order_response = trading_client.submit_order(order_data=market_order)
    
    except APIError as api_err:
        print(f"Alpaca API error: {api_err}")
        return None
    except Exception as e:
        print(f"An unexpected error occured: {e}")
        return None

    return order_response


def open_trade_alpaca(trade):
    """
    Returns True if successful, False if not
    """
    if CLOSE_POSITION_WITH_SLTP:
        print("\n\nOpening a long position, with stop loss / take profit")
        order_response = prepare_and_submit_bracket_order(trade.take_profit_price, trade.stop_loss_price)
        if order_response:
            log_trade_info(trade.take_profit_price, trade.stop_loss_price, order_response)
            trade.alpaca_order_id = str(order_response.id)
        else:
            logging.error(f"Failed to submit order for {TICKER}")
            logging.error(f"A buy signal has been missed")
            return False

    else:
        print("\n\nOpening a long position")
        order_response = prepare_and_submit_open_long_order()
        if order_response:
            log_trade_info(0.0, 0.0, order_response)
            trade.alpaca_order_id = str(order_response.id)
        else:
            logging.error(f"Failed to submit order for {TICKER}")
            logging.error(f"A buy signal has been missed")
            return False

    return True


# ********* CLOSING TRADES ********** #

def close_alpaca_trade(trade):
    """
    First attempts to close by order id, if this fails it attempts to close all open positions.
    """
    close_trade_successful = close_trade_by_order_id(trade)
    if close_trade_successful:
        print(trade)
        return True
    else:
        close_all_success = close_all_trades_alpaca()
        if not close_all_success:
            print("\nURGENT: Bot has failed to close the trade, please make a manual intervention as the trade is still open!")
            return False
    return True


def close_position(open_order):
    try:
        # Place a market sell order to close the position
        sell_order = trading_client.submit_order(
            symbol=open_order.symbol,
            qty=open_order.qty,
            side=OrderSide.SELL,
            type=OrderType.MARKET,
            time_in_force=time_in_force
        )
        return sell_order
    except Exception as e:
        logging.error(f"Error placing sell order: {e}")
        return None


def close_trade_by_order_id(trade):
    try:
        open_order = get_order_details_by_id(trade.alpaca_order_id)
        
        if open_order:
            sell_order = close_position(open_order)
            if sell_order:
                logging.info(f"Successfully placed sell order to close position. Order ID: {sell_order.id}")
                return True
            else:
                logging.error("Failed to place sell order.")
                return False
        else:
            logging.error(f"No open position found for ticker: {TICKER}")
            return False

    except Exception as e:
        logging.error(f"Error closing trade by order ID: {e}")
        return False


def close_all_trades_alpaca():
    try:
        print("Attempting to close all trades")
        trading_client.close_all_positions()
        print("Closed all trades")
        return True

    except APIError as api_err:
        # Handle Alpaca-specific API errors
        print(f"Alpaca API error: {api_err.message}")
        return False

    except ConnectionError:
        # Handle network-related errors
        print("Network error: Unable to connect to Alpaca API.")
        return False

    except Exception as e:
        # Handle any other general exceptions
        print(f"An unexpected error occurred: {e}")
        return False


# ********* GETTING OPEN POSITIONS ********** #

def get_and_show_open_positions():
    portfolio = trading_client.get_all_positions()
    for position in portfolio:
        print("{} shares of {}".format(position.qty, position.symbol))
    return portfolio

def get_order_details_by_id(order_id):
    try:
        order_details = trading_client.get_order_by_id(order_id)
        return order_details
    except Exception as e:
        logging.error(f"Error retrieving order details: {e}")
        return None

def get_position_for_ticker():
    open_position = trading_client.get_open_position(TICKER)
    return open_position

def get_open_position():
    positions = trading_client.list_positions()
    for position in positions:
        if position.symbol == TICKER:
            return position
    return None

def get_current_buying_power():
    account = trading_client.get_account()
    buying_power = float(account.buying_power)
    print(f"Current buying power: {buying_power}")
    return buying_power



# ********* LOGIC TO READ AND EXECUTE USING SIGNALS ********** #

def analyse_latest_alpaca_bar(trading_session, trade, latest_bar):

    if trade is None:
        if latest_bar['Combined_Signal'] == 1: # Open Long with buy signal
            trade = open_trade(latest_bar['Datetime'], latest_bar['Close'], latest_bar['ATR'])
            open_trade_successful = open_trade_alpaca(trade)
            if not open_trade_successful:
                trade = None    

    elif trade is not None:
        if latest_bar['Combined_Signal'] == -1: # Close Long with sell signal
            close_success = close_alpaca_trade(trade)
            if close_success:
                trading_session.add_trade(trade.close_trade(latest_bar['Datetime'], latest_bar['Close'], "Reached sell signal"))
                trade = None
        elif CLOSE_POSITION_WITH_SLTP:
            if latest_bar['High'] >= trade.take_profit_price: # Close Long with take profit
                close_success = close_alpaca_trade(trade)
                if close_success:
                    trading_session.add_trade(trade.close_trade(latest_bar['Datetime'], latest_bar['Close'], "Reached take profit"))
                    trade = None
            elif latest_bar['Low'] <= trade.stop_loss_price: # Close Long with stop loss
                close_success = close_alpaca_trade(trade)
                if close_success:
                    trading_session.add_trade(trade.close_trade(latest_bar['Datetime'], latest_bar['Close'], "Reached stop loss"))
                    trade = None

    return trade, trading_session


if __name__ == "__main__":
    print("\n\nOpening a long position")
    order_response = prepare_and_submit_open_long_order()
    if order_response:
        log_trade_info(0.0, 0.0, order_response)
    else:
        logging.error(f"Failed to submit order for {TICKER}")