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
training_period_start = '2024-08-01'
training_period_end = '2024-08-25'
unseen_period_start = '2024-08-25'
unseen_period_end = '2024-08-30'

# Choose interval
yfinance_interval = '5m'
alpaca_interval = TimeFrame.Minute

# ML parameter optimisation parameters
number_of_trials = 75


# Objectives - Only two can be chosen at the moment
multi_objective = True
profit_objective = True
num_winning_trades_objectice = True
sharpe_ratio_objective = False
normalised_profit = False

# Performance metric
risk_free_rate = 0.01
winning_trades_param = 2.5