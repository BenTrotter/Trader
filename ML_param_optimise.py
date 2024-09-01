from globals import *
import optuna
from back_tester import fetch_historic_yfinance_data, backtest_strategy
from combined_strategy import combined_strategy
from indicator_filter import *
from indicator_setup import *
from indicator_trigger import *

# Fetch historical data once
df = fetch_historic_yfinance_data(training_period_start, training_period_end, yfinance_interval)

filter_dict = {0 : generate_SMA_filter_signal }


setup_dict = {0 : generate_RSI_setup_signal}
trigger_dict = {0 : generate_MACD_trigger_signal}

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
    filter_range = trial.suggest_int('filter key', 0 ,0)
    setup_range = trial.suggest_int('setup key', 0 ,0)
    trigger_range = trial.suggest_int('trigger key', 0 ,0)

    filter_params = {'sma_window': 50, 'look_back_period': 3},
    setup_params = {'period': 14, 'overbought_condition': 70, 'oversold_condition': 30},
    trigger_params = {'fast_period': 12, 'slow_period': 26, 'signal_period': 9}

    # Create strategy instance with suggested parameters
    strategy = combined_strategy(
        df.copy(),
        filter_func=filter_dict.get(filter_range),
        setup_func=setup_dict.get(setup_range), 
        trigger_func=trigger_dict.get(trigger_range),
        f = filter_dict.get(filter_range).get(filter_range),
        filter_params={'sma_window': 50, 'look_back_period': 3},
        setup_params={'period': 14, 'overbought_condition': 70, 'oversold_condition': 30},
        trigger_params={'fast_period': 12, 'slow_period': 26, 'signal_period': 9})
    #     sma_window, 
    #     look_back_period, 
    #     period, 
    #     overbought_condition, 
    #     oversold_condition, 
    #     fast_period, 
    #     slow_period, 
    #     signal_period
    # )

    # Backtest strategy
    profit_percent = backtest_strategy(False, strategy)
    
    # We want to maximize profit, so we return negative profit
    return -profit_percent

if __name__ == "__main__":
    # Create a study object to minimize the objective function
    study = optuna.create_study(direction='minimize')
    
    # Optimize the objective function
    study.optimize(objective, n_trials=number_of_trials)  # You can adjust the number of trials

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

    sma_window = study.best_params.get("sma_window")
    look_back_period= study.best_params.get("look_back_period")
    period = study.best_params.get("period")
    overbought_condition = study.best_params.get("overbought_condition")
    oversold_condition = study.best_params.get("oversold_condition")
    fast_period = study.best_params.get("fast_period")
    slow_period = study.best_params.get("slow_period")
    signal_period = study.best_params.get("signal_period")
    df = SMA_RSI_MACD_Strat(df, sma_window, look_back_period, period, overbought_condition, oversold_condition, fast_period, slow_period, signal_period)
    backtest_strategy(True, df)
