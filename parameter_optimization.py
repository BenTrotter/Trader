import optuna
from back_tester import fetch_historic_yfinance_data, backtest_strategy
from trading_strategy_v1 import SMA_RSI_MACD_Strat

# Fetch historical data once
ticker = 'AAPL'
data_period = "5d"
data_interval = "1m"
data = fetch_historical_data(ticker, data_period, data_interval)

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
        data.copy(), 
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

if __name__ == "__main__":
    # Create a study object to minimize the objective function
    study = optuna.create_study(direction='minimize')
    
    # Optimize the objective function
    study.optimize(objective, n_trials=100)  # You can adjust the number of trials

    # Print best parameters and best value
    print("Best parameters: ", study.best_params)
    print("Best profit (negative): ", study.best_value)

    # Plot optimization history and parameter importances
    import optuna.visualization

    # Plot optimization history
    fig = optuna.visualization.plot_optimization_history(study)
    fig.show()

    # Plot parameter importances
    fig = optuna.visualization.plot_param_importances(study)
    fig.show()


