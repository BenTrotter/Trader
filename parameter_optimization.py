import optuna
from back_tester import fetch_historic_yfinance_data, backtest_strategy
from trading_strategy_v1 import SMA_RSI_MACD_Strat

def objective(trial):
    # Define parameter ranges for optimization
    sma_window = trial.suggest_int('sma_window', 10, 100)
    look_back_period = trial.suggest_int('look_back_period', 1, 30)
    period = trial.suggest_int('period', 5, 30)
    overbought_condition = trial.suggest_int('overbought_condition', 60, 80)
    oversold_condition = trial.suggest_int('oversold_condition', 20, 40)
    fast_period = trial.suggest_int('fast_period', 5, 15)
    slow_period = trial.suggest_int('slow_period', 12, 26)
    signal_period = trial.suggest_int('signal_period', 5, 12)

    # Fetch historical data
    ticker = 'AMZN'
    data_period = "5d"
    data_interval = "1m"
    data = fetch_historic_yfinance_data(ticker, data_period, data_interval)

    # Create strategy instance with suggested parameters
    strategy = SMA_RSI_MACD_Strat(
        data, 
        sma_window, 
        look_back_period, 
        period, 
        overbought_condition, 
        oversold_condition, 
        fast_period, 
        slow_period, 
        signal_period
    )

    # Backtest strategy
    profit_percent = backtest_strategy(strategy)
    
    # We want to maximize profit, so we return negative profit
    return -profit_percent


study = optuna.create_study(direction='minimize')
study.optimize(objective, n_trials=20)  # You can adjust the number of trials

print("Best parameters: ", study.best_params)
print("Best profit (negative): ", study.best_value)

optuna.visualization.plot_optimization_history(study)

optuna.visualization.plot_param_importances(study)
