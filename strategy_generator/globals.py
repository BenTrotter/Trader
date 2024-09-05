from alpaca.data.timeframe import TimeFrame


# Choose stock or crypto
STOCK = False
TICKER = "AMZN"

CRYPTO = True
CRYPTO_TICKER = "BTC/USD"

# The quantity and starting balance to trade with
QUANTITY = 0.017
STARTING_BALANCE = 1000

# Choose a data source
YFINANCE_DATA_SOURCE = False
ALPACA_DATA_SOURCE = True

# Choose dates
TRAINING_PERIOD_START = '2024-09-01'
TRAINING_PERIOD_END = '2024-09-03'
UNSEEN_PERIOD_START = '2024-09-03'
UNSEEN_PERIOD_END = '2024-09-04'

# Choose interval
YFINANCE_INTERVAL = '5m'
ALPACA_INTERVAL = TimeFrame.Minute

# ML parameter optimisation parameters
NUMBER_OF_TRIALS = 100

# Objectives - Only two can be chosen at the moment
MULTI_OBJECTIVE = True
NORMALISED_PROFIT = True
SHARPE_RATIO_OBJECTIVE = False
NUM_WINNING_TRADES_OBJECTIVE = True

# Objectives - objective weighting
WEIGHT_OBJECTIVE_1 = 0.5
WEIGHT_OBJECTIVE_2 = 0.5

# Performance metric
RISK_FREE_RATE = 0.021
WINNING_TRADES_PARAM = 4

# Take profit / stop loss calculation method and parameters
CLOSE_POSITION_WITH_SLTP = True # Boolean to set whether trades can be closed with sl/tp or only sell signal
RISK_REWARD_RATIO = 4 # sets the take profit / stop loss ratio
ATR_MULTIPLIER = 1.5 # sets the multiple of the average true range to calculate the stop loss

# Choose period for ATR
ATR_PERIOD = 10

# Parameter optimisation float precision
FLOAT_PRECISION = 0.01

# Stock picker parameters
TRAINING_PERIOD_STOCKPICK_START = '2024-01-01' # Need to be longer period
STOCK_PICKER_VALIDATION_DATE = '2024-08-30'