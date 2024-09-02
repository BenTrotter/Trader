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
training_period_start = '2024-05-19'
training_period_end = '2024-05-29'
unseen_period_start = '2024-05-29'
unseen_period_end = '2024-05-30'

# Choose interval
yfinance_interval = '5m'
alpaca_interval = TimeFrame.Minute

# ML parameter optimisation parameters
number_of_trials = 100


# Objectives - Only two can be chosen at the moment
multi_objective = True
normalised_profit = True
sharpe_ratio_objective = True
num_winning_trades_objectice = False

# Objectives - objective weighting (Edit trading_session.get_objectives() 
# in order to choose which weighting is for which objective)
weight_objective_1 = 0.6
weight_objective_2 = 0.4


# Performance metric
risk_free_rate = 0.021
winning_trades_param = 8

# Parameter optimisation float precision
float_precision = 0.01