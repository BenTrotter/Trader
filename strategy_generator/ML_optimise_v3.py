from globals import *
import optuna
import optuna.visualization as vis
import numpy as np
import pandas as pd
from tabulate import tabulate
from back_tester import backtest_strategy, backtest_strategy_returning_metrics
from combined_strategy import combined_strategy
from indicator_filter import *
from indicator_setup import *
from indicator_trigger import *
from indicator_param_dictionary import *


def objective(trial):

    # Select a filter function
    filter_func_name = trial.suggest_categorical('filter_func', list(functions_info['filter_functions'].keys()))
    filter_func_info = functions_info['filter_functions'][filter_func_name]
    filter_func = filter_func_info['function']
    
    # Select a setup function
    setup_func_name = trial.suggest_categorical('setup_func', list(functions_info['setup_functions'].keys()))
    setup_func_info = functions_info['setup_functions'][setup_func_name]
    setup_func = setup_func_info['function']
    
    # Select a trigger function
    trigger_func_name = trial.suggest_categorical('trigger_func', list(functions_info['trigger_functions'].keys()))
    trigger_func_info = functions_info['trigger_functions'][trigger_func_name]
    trigger_func = trigger_func_info['function']

    # Dynamically suggest parameters for each selected function
    filter_params = {}
    setup_params = {}
    trigger_params = {}

    for param_name, (param_type, start, end) in filter_func_info['params'].items():
        if param_type == 'int':
            filter_params[param_name] = trial.suggest_int(f'filter_{filter_func_name}_{param_name}', start, end)
        elif param_type == 'float':
            filter_params[param_name] = trial.suggest_float(f'filter_{filter_func_name}_{param_name}', start, end, step=FLOAT_PRECISION)

    for param_name, (param_type, start, end) in setup_func_info['params'].items():
        if param_type == 'int':
            setup_params[param_name] = trial.suggest_int(f'setup_{setup_func_name}_{param_name}', start, end)
        elif param_type == 'float':
            setup_params[param_name] = trial.suggest_float(f'setup_{setup_func_name}_{param_name}', start, end, step=FLOAT_PRECISION)

    for param_name, (param_type, start, end) in trigger_func_info['params'].items():
        if param_type == 'int':
            trigger_params[param_name] = trial.suggest_int(f'trigger_{trigger_func_name}_{param_name}', start, end)
        elif param_type == 'float':
            trigger_params[param_name] = trial.suggest_float(f'trigger_{trigger_func_name}_{param_name}', start, end, step=FLOAT_PRECISION)


    # Create strategy instance with selected functions and suggested parameters
    strategy_df = combined_strategy(
        df.copy(),
        filter_func,
        setup_func,
        trigger_func,
        filter_params=filter_params,
        setup_params=setup_params,
        trigger_params=trigger_params
    )

    # Backtest strategy
    if MULTI_OBJECTIVE:
        # Define weightings for each objective
        weight_1 = WEIGHT_OBJECTIVE_1
        weight_2 = WEIGHT_OBJECTIVE_2

        objective_1, objective_2 = backtest_strategy(False, False, strategy_df)
        
        # Apply the weightings
        weighted_objective_1 = weight_1 * objective_1
        weighted_objective_2 = weight_2 * objective_2
        
        return weighted_objective_1, weighted_objective_2
    else:
        objective_1 = backtest_strategy(False, False, strategy_df)
        return objective_1


def select_best_from_pareto(study):
    """
    Selects the best trial from the Pareto front based on the Euclidean distance to an ideal point.
    This point is assumed to have the maximum possible values for all objectives.
    
    Args:
        study (optuna.Study): The Optuna study object.
    
    Returns:
        optuna.trial.FrozenTrial: The selected trial from the Pareto front.
    """
    # Extract the Pareto front trials
    pareto_trials = study.best_trials
    
    # Calculate the ideal point (hypothetically the maximum for each objective)
    ideal_point = np.max([trial.values for trial in pareto_trials], axis=0)
    
    # Calculate the Euclidean distance of each Pareto trial from the ideal point
    distances = []
    for trial in pareto_trials:
        distance = np.linalg.norm(np.array(trial.values) - ideal_point)
        distances.append(distance)
    
    # Find the trial with the minimum distance to the ideal point
    best_index = np.argmin(distances)
    return pareto_trials[best_index]


def run_validation_on_pareto_front(study):
    if MULTI_OBJECTIVE:
        # Handle multi-objective case
        print("\nPareto front trials:")
        for trial in study.best_trials:
            print(f"Trial #{trial.number}: Values = {trial.values}, Params = {trial.params}")

        print(f"\n\nThere are {len(study.best_trials)} strategies on the Pareto front\n")

        # Rerun all Pareto front trials on the unseen data
        unseen_data_set = []
        unseen_data_1 = fetch_data('Unseen 1')
        unseen_data_set.append(unseen_data_1)
        unseen_data_2 = fetch_data('Unseen 2')
        unseen_data_set.append(unseen_data_2)
        unseen_data_3 = fetch_data('Unseen 3')
        unseen_data_set.append(unseen_data_3)

        # Lists to store results for each trial
        results_profit = []  # Results for Normalized Profit

        # Store Buy and Hold results for only one run (since they are the same for each trial)
        buy_and_hold_values = []

        count = 1
        for trial in study.best_trials:
            print(f"\n***************** Pareto front strategy {count} ************************\n")
            trial_params = trial.params

            best_filter_func_name = trial_params['filter_func']
            best_setup_func_name = trial_params['setup_func']
            best_trigger_func_name = trial_params['trigger_func']

            best_filter_func = functions_info['filter_functions'][best_filter_func_name]['function']
            best_setup_func = functions_info['setup_functions'][best_setup_func_name]['function']
            best_trigger_func = functions_info['trigger_functions'][best_trigger_func_name]['function']

            best_filter_params = {k.replace(f'filter_{best_filter_func_name}_', ''): v 
                                  for k, v in trial_params.items() if k.startswith(f'filter_{best_filter_func_name}_')}
            best_setup_params = {k.replace(f'setup_{best_setup_func_name}_', ''): v 
                                 for k, v in trial_params.items() if k.startswith(f'setup_{best_setup_func_name}_')}
            best_trigger_params = {k.replace(f'trigger_{best_trigger_func_name}_', ''): v 
                                   for k, v in trial_params.items() if k.startswith(f'trigger_{best_trigger_func_name}_')}

            trial_profit = {'Trial #': count}
            signaled_data_set = []
            for unseen_data in unseen_data_set:
                unseen_strategy_df = combined_strategy(
                    unseen_data.copy(), 
                    best_filter_func, 
                    best_setup_func, 
                    best_trigger_func, 
                    filter_params=best_filter_params, 
                    setup_params=best_setup_params, 
                    trigger_params=best_trigger_params
                )
                signaled_data_set.append(unseen_strategy_df)

            print("\nBest filter function: ", best_filter_func_name)
            print("Best setup function: ", best_setup_func_name)
            print("Best trigger function: ", best_trigger_func_name)
            print("\nBest filter parameters: ", best_filter_params)
            print("Best setup parameters: ", best_setup_params)
            print("Best trigger parameters: ", best_trigger_params)
            print("\n")

            # Collect Buy and Hold results only once, since they're identical across trials
            if count == 1:
                for signaled_data in signaled_data_set:
                    buy_and_hold, _ = backtest_strategy_returning_metrics(signaled_data)
                    buy_and_hold_values.append(buy_and_hold)

            # Backtest and collect profit % for each trial
            itr = 1
            normalized_profit_values = []
            for signaled_data in signaled_data_set:
                print(f"Unseen data trial {itr}")
                backtest_strategy(False, True, signaled_data)
                _, normalised_profit = backtest_strategy_returning_metrics(signaled_data)
                normalized_profit_values.append(normalised_profit)
                
                # Add profit results to trial_profit
                trial_profit[f'Unseen {itr} Profit %'] = normalised_profit
                itr += 1

            # Calculate and add averages to trial_profit
            trial_profit['Average Profit %'] = round(np.mean(normalized_profit_values), 2)
            results_profit.append(trial_profit)

            print("\n******************************************************************\n")
            count += 1

        # Create a pandas DataFrame for Normalized Profit results
        df_profit = pd.DataFrame(results_profit)

        # Create a separate DataFrame for Buy and Hold results (shown once)
        df_bnh = pd.DataFrame([buy_and_hold_values], columns=[f'   Unseen {i+1} B&H  ' for i in range(len(buy_and_hold_values))])
        df_bnh['  Average B&H   '] = round(np.mean(buy_and_hold_values), 2)

        # Print the Buy and Hold table (only once)
        print("\nFinal Results:\n")
        print(tabulate(df_bnh, headers='keys', tablefmt='grid'))
        # Print the Profit % table (one row per trial)
        print(tabulate(df_profit.drop(columns='Trial #'), headers='keys', tablefmt='grid'))
        print("\n\n")





if __name__ == "__main__":

    df = fetch_data('Training')

    # Create a study object depending on the optimization type
    if MULTI_OBJECTIVE:
        study = optuna.create_study(directions=['maximize', 'maximize'])
    else:
        study = optuna.create_study(direction='maximize')
    
    # Optimize the objective function
    study.optimize(objective, n_trials=NUMBER_OF_TRIALS)

    if MULTI_OBJECTIVE:
        # Handle multi-objective case
        print("Pareto front trials:")
        for trial in study.best_trials:
            print(f"Trial #{trial.number}: Values = {trial.values}, Params = {trial.params}")

        # Plot Pareto front
        fig = vis.plot_pareto_front(study)
        fig.show()


        run_validation_on_pareto_front(study)
 
    else:
        # Handle single-objective case
        print("Best parameters: ", study.best_params)
        print("Best value (maximized): ", study.best_value)

        # Plot optimization history and parameter importances
        fig = vis.plot_optimization_history(study)
        fig.show()

        fig = vis.plot_param_importances(study)
        fig.show()

        best_params = study.best_params
