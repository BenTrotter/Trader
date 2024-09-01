import optuna
from back_tester import fetch_historic_yfinance_data, backtest_strategy
from combined_strategy import combined_strategy
from indicator_filter import *
from indicator_setup import *
from indicator_trigger import *
from indicator_param_dictionary import *

# # Define available functions and their parameter ranges
# functions_info = {
#     'filter_functions': {
#         'generate_SMA_filter_signal': {
#             'function': generate_SMA_filter_signal,
#             'params': {
#                 'sma_window': ('int', 10, 50),
#                 'look_back_period': ('int', 1, 10)
#             }
#         }
#         # Add more filter functions as needed
#     },
#     'setup_functions': {
#         'generate_RSI_setup_signal': {
#             'function': generate_RSI_setup_signal,
#             'params': {
#                 'period': ('int', 5, 30),
#                 'overbought_condition': ('int', 60, 100),
#                 'oversold_condition': ('int', 0, 40)
#             }
#         }
#         # Add more setup functions as needed
#     },
#     'trigger_functions': {
#         'generate_MACD_trigger_signal': {
#             'function': generate_MACD_trigger_signal,
#             'params': {
#                 'fast_period': ('int', 3, 40),
#                 'slow_period': ('int', 12, 60),
#                 'signal_period': ('int', 5, 30),
#             }
#         }
#         # Add more trigger functions as needed
#     }
# }


df = fetch_historic_yfinance_data(training_period_start, training_period_end, yfinance_interval)

def objective(trial):
    # Dynamically suggest parameters based on functions_info
    params = {}
    
    for category in functions_info:
        for func_name, func_info in functions_info[category].items():
            for param_name, param_info in func_info['params'].items():
                param_type, param_min, param_max = param_info
                full_param_name = f"{func_name}_{param_name}"
                if param_type == 'int':
                    params[full_param_name] = trial.suggest_int(full_param_name, param_min, param_max)
                elif param_type == 'float':
                    params[full_param_name] = trial.suggest_float(full_param_name, param_min, param_max)
    
    # Extract function names and their best parameters dynamically
    filter_func_name = list(functions_info['filter_functions'].keys())[0]  # Example: first filter function
    setup_func_name = list(functions_info['setup_functions'].keys())[0]    # Example: first setup function
    trigger_func_name = list(functions_info['trigger_functions'].keys())[0] # Example: first trigger function
    
    filter_func = functions_info['filter_functions'][filter_func_name]['function']
    setup_func = functions_info['setup_functions'][setup_func_name]['function']
    trigger_func = functions_info['trigger_functions'][trigger_func_name]['function']
    
    # Get parameters for each function
    filter_params = {param: params[f"{filter_func_name}_{param}"] for param in functions_info['filter_functions'][filter_func_name]['params']}
    setup_params = {param: params[f"{setup_func_name}_{param}"] for param in functions_info['setup_functions'][setup_func_name]['params']}
    trigger_params = {param: params[f"{trigger_func_name}_{param}"] for param in functions_info['trigger_functions'][trigger_func_name]['params']}
    
    # Create strategy instance with suggested parameters
    strategy = combined_strategy(
        df=df.copy(),
        filter_func=filter_func,
        setup_func=setup_func,
        trigger_func=trigger_func,
        filter_params=filter_params,
        setup_params=setup_params,
        trigger_params=trigger_params
    )

    # Backtest strategy
    profit_percent = backtest_strategy(False, strategy)
    
    # We want to maximize profit, so we return negative profit
    return profit_percent

if __name__ == "__main__":
    # Create a study object to minimize the objective function
    study = optuna.create_study(direction='maximize')
    
    # Optimize the objective function
    study.optimize(objective, n_trials=number_of_trials)  # You can adjust the number of trials

    # Plot optimization history
    fig = optuna.visualization.plot_optimization_history(study)
    fig.show()

    # # Plot parameter importances
    # fig = optuna.visualization.plot_param_importances(study)
    # fig.show()

    # Print best parameters and best value
    print("Best parameters: ", study.best_params)
    print("Best profit (negative): ", study.best_value)

    # Dynamically construct best parameters using functions_info
    best_filter_params = {}
    best_setup_params = {}
    best_trigger_params = {}

    # Extracting the best params using the functions_info
    for func_name, func_info in functions_info['filter_functions'].items():
        best_filter_params = {param: study.best_params.get(f"{func_name}_{param}") for param in func_info['params']}
    
    for func_name, func_info in functions_info['setup_functions'].items():
        best_setup_params = {param: study.best_params.get(f"{func_name}_{param}") for param in func_info['params']}
    
    for func_name, func_info in functions_info['trigger_functions'].items():
        best_trigger_params = {param: study.best_params.get(f"{func_name}_{param}") for param in func_info['params']}
    
    print("Best filter parameters: ", best_filter_params)
    print("Best setup parameters: ", best_setup_params)
    print("Best trigger parameters: ", best_trigger_params)

    # Retrieve the best function names from the study's best parameters
    best_filter_func_name = list(functions_info['filter_functions'].keys())[0]  # Placeholder for actual best selection logic
    best_setup_func_name = list(functions_info['setup_functions'].keys())[0]    # Placeholder for actual best selection logic
    best_trigger_func_name = list(functions_info['trigger_functions'].keys())[0] # Placeholder for actual best selection logic

    best_filter_func = functions_info['filter_functions'][best_filter_func_name]['function']
    best_setup_func = functions_info['setup_functions'][best_setup_func_name]['function']
    best_trigger_func = functions_info['trigger_functions'][best_trigger_func_name]['function']

    # Run backtest with the best parameters
    best_strategy_df = combined_strategy(
        df=df.copy(),
        filter_func=best_filter_func,
        setup_func=best_setup_func,
        trigger_func=best_trigger_func,
        filter_params=best_filter_params,
        setup_params=best_setup_params,
        trigger_params=best_trigger_params
    )

    # Evaluate strategy performance with the best parameters
    final_profit = backtest_strategy(True, best_strategy_df)
    print("Final profit with best parameters: ", final_profit)
