from alpaca.data.timeframe import TimeFrame


# Choose stock or crypto
stock = True
ticker = "AMZN"

crypto = False
crypto_ticker = "BTC/USD"

# The quantity and starting balance to trade with
quantity = 6
starting_balance = 1000

# Choose a data source
yfinance_data_source = True
alpaca_data_source = False

# Choose dates
training_period_start = '2024-07-20'
training_period_end = '2024-08-20'
unseen_period_start = '2024-08-20'
unseen_period_end = '2024-08-27'

# Choose interval
yfinance_interval = '5m'
alpaca_interval = TimeFrame.Minute

# ML parameter optimisation parameters
number_of_trials = 600
