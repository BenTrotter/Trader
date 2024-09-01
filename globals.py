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
training_period_start = '2024-08-20'
training_period_end = '2024-08-25'
unseen_period_start = '2024-08-25'
unseen_period_end = '2024-08-26'

# Choose interval
yfinance_interval = '5m'
alpaca_interval = TimeFrame.Minute

# ML parameter optimisation parameters
number_of_trials = 40
