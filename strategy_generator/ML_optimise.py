from globals import *
import optuna
import optuna.visualization as vis
import numpy as np
from back_tester import backtest_strategy
from combined_strategy import combined_strategy
from indicator_filter import *
from indicator_setup import *
from indicator_trigger import *
from strategy_generator.indicator_param_dict_intra import *


def objective(trial):

    # Select a filter function
    filter_func_name = trial.suggest_categorical('filter_func', list(intra_functions_info['filter_functions'].keys()))
    filter_func_info = intra_functions_info['filter_functions'][filter_func_name]
    filter_func = filter_func_info['function']
    
    # Select a setup function
    setup_func_name = trial.suggest_categorical('setup_func', list(intra_functions_info['setup_functions'].keys()))
    setup_func_info = intra_functions_info['setup_functions'][setup_func_name]
    setup_func = setup_func_info['function']
    
    # Select a trigger function
    trigger_func_name = trial.suggest_categorical('trigger_func', list(intra_functions_info['trigger_functions'].keys()))
    trigger_func_info = intra_functions_info['trigger_functions'][trigger_func_name]
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

        # Select the best trial based on distance to an ideal point
        best_trial = select_best_from_pareto(study)
        best_params = best_trial.params
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

    # Retrieve best function names and parameters
    best_filter_func_name = best_params['filter_func']
    best_setup_func_name = best_params['setup_func']
    best_trigger_func_name = best_params['trigger_func']

    best_filter_func = intra_functions_info['filter_functions'][best_filter_func_name]['function']
    best_setup_func = intra_functions_info['setup_functions'][best_setup_func_name]['function']
    best_trigger_func = intra_functions_info['trigger_functions'][best_trigger_func_name]['function']

    # Extract best parameters, removing the function prefixes but keeping parameter names intact
    best_filter_params = {k.replace(f'filter_{best_filter_func_name}_', ''): v 
                          for k, v in best_params.items() if k.startswith(f'filter_{best_filter_func_name}_')}
    best_setup_params = {k.replace(f'setup_{best_setup_func_name}_', ''): v 
                         for k, v in best_params.items() if k.startswith(f'setup_{best_setup_func_name}_')}
    best_trigger_params = {k.replace(f'trigger_{best_trigger_func_name}_', ''): v 
                           for k, v in best_params.items() if k.startswith(f'trigger_{best_trigger_func_name}_')}

    # Print the separated parameters to confirm correct extraction
    print("\nBest filter parameters: ", best_filter_params)
    print("Best setup parameters: ", best_setup_params)
    print("Best trigger parameters: ", best_trigger_params)


    # Re-run with the best parameters to see how it performed
    best_strategy_df = combined_strategy(
        df.copy(), 
        best_filter_func, 
        best_setup_func, 
        best_trigger_func, 
        filter_params=best_filter_params, 
        setup_params=best_setup_params, 
        trigger_params=best_trigger_params
    )
    
    backtest_strategy(True, True, best_strategy_df)

    unseen_data = fetch_data('Unseen')

    unseen_strategy_df = combined_strategy(
        unseen_data, 
        best_filter_func, 
        best_setup_func, 
        best_trigger_func, 
        filter_params=best_filter_params, 
        setup_params=best_setup_params, 
        trigger_params=best_trigger_params
    )

    backtest_strategy(True, True, unseen_strategy_df)

    # Print the separated parameters at the end to confirm correct extraction and to populate bot
    print("\nBest filter function: ", best_filter_func_name)
    print("Best setup function: ", best_setup_func_name)
    print("Best trigger function: ", best_trigger_func_name)
    print("\nBest filter parameters: ", best_filter_params)
    print("Best setup parameters: ", best_setup_params)
    print("Best trigger parameters: ", best_trigger_params)