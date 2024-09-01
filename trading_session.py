from globals import *
from datetime import datetime
from tabulate import tabulate
import numpy as np

class Trading_session:
    def __init__(self, 
                 starting_balance: float,
                 ):
        self.starting_balance = starting_balance
        self.current_balance = starting_balance
        self.trades= []
        self.average_duration_of_trade = ""
        self.percentage_change_of_strategy = 0.0
        self.number_of_winning_trades = 0
        self.normalized_profit = 0.0
        self.sharpe_ratio = 0.0


    def add_trade(self, trade):
        self.trades.append(trade)
        self.update_balance(trade)


    def update_balance(self, trade):
        self.current_balance += trade.profit


    def display_trades(self):
        total_profit = 0
        for tr in self.trades:
            total_profit = tr.profit + total_profit
            print(tr)


    def calculate_percentage_change_of_strategy(self):
        self.percentage_change_of_strategy = (self.current_balance - self.starting_balance) * 100 / self.starting_balance


    def calculate_average_duration(self):
        # Check if the trades list is empty
        if not self.trades:
            return "00:00:00"  # or return None, or raise an exception as per your needs

        # Calculate total duration in seconds
        total_seconds = sum(trade.calculate_duration_in_seconds() for trade in self.trades)
        
        # Calculate average duration in seconds
        average_seconds = total_seconds / len(self.trades)
        
        # Convert average duration to HH:MM:SS format
        hours = int(average_seconds // 3600)
        minutes = int((average_seconds % 3600) // 60)
        seconds = int(average_seconds % 60)
        
        self.average_duration_of_trade = f"{hours:02}:{minutes:02}:{seconds:02}"


    def calculate_number_of_winning_trades(self):
        count = 0
        for tr in self.trades:
            if tr.profit > 0:
                count += 1
        self.number_of_winning_trades = count


    def calculate_normalized_profit(self):
        # Normalized profit can be calculated as total profit divided by the starting balance
        normalized_profit = (self.current_balance - self.starting_balance) / self.starting_balance
        self.normalized_profit = normalized_profit
    

    def calculate_sharpe_ratio(self):
        """
        Calculate the Sharpe Ratio for the trading session.
        
        The Sharpe Ratio is calculated as the ratio of the excess return (returns over the risk-free rate)
        to the standard deviation of the returns. A higher Sharpe Ratio indicates a better risk-adjusted return.
        
        Args:
            risk_free_rate (float): The risk-free rate to compare against. Defaults to 0.01 (1%).
        
        Returns:
            float: The Sharpe Ratio, or 0 if it cannot be calculated.
        """
        # Extract the profit percentages from the trades
        returns = np.array([trade.profit_pct for trade in self.trades])

        # Check if returns array is empty or contains only zeros
        if returns.size == 0 or np.all(returns == 0):
            return 0.0

        # Calculate the mean return
        mean_return = np.mean(returns) / 100

        # Calculate the excess return over the risk-free rate
        excess_return = mean_return - risk_free_rate

        # Calculate the standard deviation of returns
        std_dev = np.std(returns) / 100

        # Handle cases where standard deviation is zero
        if std_dev == 0:
            return 0.0 if excess_return <= 0 else float('inf')

        # Calculate and return the Sharpe Ratio
        sharpe_ratio = excess_return / std_dev
        self.sharpe_ratio = sharpe_ratio

    
    def get_objectives(self):
        results = []  
        
        if profit_objective:
            results.append(self.percentage_change_of_strategy)
        
        if num_winning_trades_objectice:
            results.append(self.number_of_winning_trades)
        
        if sharpe_ratio_objective:
            results.append(self.sharpe_ratio)
        
        if normalised_profit:
            results.append(self.normalized_profit)
        
        return tuple(results)


    def __str__(self) -> str:
        return (f"\nStarting Balance: ${self.starting_balance:.2f}\n"
                f"Current Balance: ${self.current_balance:.2f}\n"
                f"Number of Trades: {len(self.trades)}\n"
                f"Number of Winning Trades: {self.number_of_winning_trades}\n"
                f"Average Trade Duration: {self.average_duration_of_trade}\n"
                f"Strategy percentage change: {self.percentage_change_of_strategy:.2f}%\n"
                f"Normalized Profit: {self.normalized_profit:.2f}%\n"
                f"Sharpe Ratio: {self.sharpe_ratio:.2f}%\n")


class Trade(Trading_session):
    
    def __init__(self,
                 open_price: float,
                 long: bool,
                 short: bool,
                 take_profit_pct: float,
                 stop_loss_pct: float,
                 close_price: float = 0,
                 open_time: datetime = None,
                 close_time: datetime = None,
                 quantity: float = 1,
                 ):
        self.open_time = open_time
        self.close_time = close_time
        self.open_price = round(open_price, 2)
        self.close_price = round(close_price, 2)
        self.quantity = quantity
        self.long = long
        self.short = short
        self.take_profit_pct = take_profit_pct
        self.stop_loss_pct = stop_loss_pct
        self.value_of_trade = self.calculate_value_of_trade()
        self.take_profit_price = self.calculate_take_profit_price()
        self.stop_loss_price = self.calculate_stop_loss_price()
        self.profit_pct = 0
        self.duration = 0
        self.profit = 0
        self.close_reason = ""
    
    def calculate_value_of_trade(self) -> float:
        """
        """
        return self.open_price * self.quantity

    def calculate_profit(self) -> float:
        """
        Calculate the profit of the trade and profit percentage
        Profit is calculated differently for long and short trades.
        For long trades, profit = (close_price - open_price) * quantity
        For short trades, profit = (open_price - close_price) * quantity
        """
        if self.long:
            profit = (self.close_price - self.open_price) * self.quantity
            profit_pct = ((self.close_price - self.open_price) / self.open_price) * 100
            return profit, profit_pct
        elif self.short:
            profit = (self.open_price - self.close_price) * self.quantity
            profit_pct = ((self.open_price - self.close_price) / self.close_price) * 100
            return profit, profit_pct
        else:
            return 0.0, 0.0
        
        
    def calculate_duration(self):
        # Calculate the duration as a timedelta object
        duration = self.close_time - self.open_time
        
        # Extract hours, minutes, and seconds from the timedelta object
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        # Format duration as HH:MM:SS
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    
    
    def calculate_duration_in_seconds(self):
        duration = self.close_time - self.open_time
        return int(duration.total_seconds())
    

    def calculate_take_profit_price(self):
        if self.long:
            take_profit_price = self.open_price * (1 + self.take_profit_pct)
        elif self.short:
            take_profit_price = self.open_price * (1 - self.take_profit_pct)
        return take_profit_price
    

    def calculate_stop_loss_price(self):
        if self.long:
            stop_loss_price = self.open_price * (1 - self.stop_loss_pct)
        elif self.short:
            stop_loss_price = self.open_price * (1 + self.stop_loss_pct)
        return stop_loss_price


    def close_trade(self, close_time, close_price, close_reason):
        self.close_time = close_time
        self.close_price = close_price
        self.profit, self.profit_pct = self.calculate_profit()
        self.duration = self.calculate_duration()
        self.close_reason = close_reason
        return self
    

    def __str__(self):
        # Prepare the data for tabulation
        print("\n")
        table_data = [
            ["Open Time", self.open_time],
            ["Close Time", self.close_time],
            ["Open Price", f"${self.open_price:.2f}"],
            ["Close Price", f"${self.close_price:.2f}"],
            ["Quantity", self.quantity],
            ["Trade Value", f"${self.value_of_trade:.2f}"],
            ["Trade Type", "Long" if self.long else "Short"],
            ["Take Profit Price", f"${self.take_profit_price:.2f}" if self.take_profit_price else "N/A"],
            ["Stop Loss Price", f"${self.stop_loss_price:.2f}" if self.stop_loss_price else "N/A"],
            ["Close Reason", self.close_reason if self.close_reason else "N/A"],
            ["Duration", self.duration],
            ["Profit", f"${self.profit:.2f}"],
            ["Profit Percentage", f"{self.profit_pct:.2f}%"]
        ]

        # Create and return the formatted table
        return tabulate(table_data, headers=["Attribute", "Value"], tablefmt="grid")

    