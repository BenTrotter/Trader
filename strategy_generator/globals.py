from alpaca.data.timeframe import TimeFrame

# Choose trading method
SWING_TRADING = True
INTRADAY_TRADING = False

# Choose stock or crypto
STOCK = True
TICKER = "MA"

CRYPTO = False # TODO: Remember to turn of stop loss / take profit if using bot with crypto
CRYPTO_TICKER = "ETH/USD"

# The quantity and starting balance to trade with
QUANTITY = 1
STARTING_BALANCE = 1000

# Choose a data source
YFINANCE_DATA_SOURCE = False
ALPACA_DATA_SOURCE = True

# Choose dates
TRAINING_PERIOD_START = '2024-05-01'
TRAINING_PERIOD_END = '2024-09-07'
UNSEEN_PERIOD_START = '2024-09-9'
UNSEEN_PERIOD_END = '2024-09-10'

# Choose interval
YFINANCE_INTERVAL = '5m'
ALPACA_INTERVAL = TimeFrame.Day

# ML parameter optimisation parameters
NUMBER_OF_TRIALS = 300

# Objectives - Only two can be chosen at the moment
MULTI_OBJECTIVE = True
NORMALISED_PROFIT = True
SHARPE_RATIO_OBJECTIVE = False
NUM_WINNING_TRADES_OBJECTIVE = True

# Objectives - objective weighting
WEIGHT_OBJECTIVE_1 = 0.6
WEIGHT_OBJECTIVE_2 = 0.4

# Performance metric
ANNUAL_RISK_FREE_RATE = 4
WINNING_TRADES_PARAM = 0

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


UNSEEN_PERIOD_START_1 = '2024-05-01'
UNSEEN_PERIOD_END_1 = '2024-09-07'

UNSEEN_PERIOD_START_2 = '2024-09-4'
UNSEEN_PERIOD_END_2 = '2024-09-5'

UNSEEN_PERIOD_START_3 = '2024-09-5'
UNSEEN_PERIOD_END_3 = '2024-09-6'

UNSEEN_PERIOD_START_4 = '2024-09-6'
UNSEEN_PERIOD_END_4 = '2024-09-7'

UNSEEN_PERIOD_START_5 = '2024-09-7'
UNSEEN_PERIOD_END_5 = '2024-09-7'