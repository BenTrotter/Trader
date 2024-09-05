from alpaca.data.timeframe import TimeFrame


# Choose stock or crypto
stock = False
ticker = "AMZN"

crypto = True
crypto_ticker = "BTC/USD"

# The quantity and starting balance to trade with
quantity = 0.017
starting_balance = 1000

# Choose a data source
yfinance_data_source = False
alpaca_data_source = True

# Choose dates
training_period_start = '2024-07-10'
training_period_end = '2024-08-27'
unseen_period_start = '2024-08-27'
unseen_period_end = '2024-08-31'

# Choose interval
yfinance_interval = '5m'
alpaca_interval = TimeFrame.Minute

# ML parameter optimisation parameters
number_of_trials = 150

# Objectives - Only two can be chosen at the moment
multi_objective = True
normalised_profit = True
sharpe_ratio_objective = True
num_winning_trades_objectice = False

# Objectives - objective weighting
weight_objective_1 = 0.6
weight_objective_2 = 0.4

# Performance metric
risk_free_rate = 0.021
winning_trades_param = 8

# Take profit / stop loss calculation method and parameters
take_profit_method_ATR = True
stop_loss_method_ATR = True
take_profit_percentage = 0.04
stop_loss_percentage = 0.02
risk_reward_ratio = 4 # sets the take profit / stop loss ratio
atr_multipler = 1.5 # sets the multiple of the average true range to calculate the stop loss

# Choose period for ATR
atr_period = 10

# Parameter optimisation float precision
float_precision = 0.01


# Stock picker parameters
training_period_stockpick_start = '2024-01-01' # Need to be longer period
stock_pick_validation_date = '2024-08-30'
