from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.base import BaseEstimator
import numpy as np
from combined_strategy import combined_strategy
from back_tester import backtest_strategy
from data_fetch import fetch_data
from indicator_param_dictionary import functions_info
from sklearn.metrics import make_scorer


class TradingStrategy(BaseEstimator):
    def __init__(self, 
                 filter_func_name=None, 
                 setup_func_name=None, 
                 trigger_func_name=None,
                 filter_params=None, 
                 setup_params=None, 
                 trigger_params=None):
        self.filter_func_name = filter_func_name
        self.setup_func_name = setup_func_name
        self.trigger_func_name = trigger_func_name
        self.filter_params = filter_params if filter_params is not None else {}
        self.setup_params = setup_params if setup_params is not None else {}
        self.trigger_params = trigger_params if trigger_params is not None else {}

    def fit(self, X, y=None):
        return self

    def score(self, X, y=None):
        """
        Score method to evaluate strategy performance.
        """
        df = combined_strategy(
            X.copy(),
            functions_info['filter_functions'][self.filter_func_name]['function'],
            functions_info['setup_functions'][self.setup_func_name]['function'],
            functions_info['trigger_functions'][self.trigger_func_name]['function'],
            filter_params=self.filter_params,
            setup_params=self.setup_params,
            trigger_params=self.trigger_params
        )

        # Perform backtest and return a performance metric (e.g., total profit)
        performance_metric = backtest_strategy(False, False, df)
        
        # Ensure the performance metric is valid and handle NaN
        if np.isnan(performance_metric) or performance_metric <= 0:
            return -np.inf  # Assign a very low score for invalid results
        
        return performance_metric


    def set_params(self, **params):
        for key, value in params.items():
            setattr(self, key, value)
        return self

    def get_params(self, deep=True):
        return {
            'filter_func_name': self.filter_func_name,
            'setup_func_name': self.setup_func_name,
            'trigger_func_name': self.trigger_func_name,
            'filter_params': self.filter_params,
            'setup_params': self.setup_params,
            'trigger_params': self.trigger_params
        }


# Custom scorer function for the trading strategy
def custom_scorer(estimator, X):
    # We expect `score` to return a valid score
    score = estimator.score(X)  # This should return a performance metric
    # Ensure score is valid; handle invalid or NaN scores
    return score if not np.isnan(score) else -np.inf

scorer = make_scorer(custom_scorer, greater_is_better=True)


from sklearn.model_selection import RandomizedSearchCV
import numpy as np

# Define the parameter grid
param_grid = {
    'filter_func_name': list(functions_info['filter_functions'].keys()),
    'setup_func_name': list(functions_info['setup_functions'].keys()),
    'trigger_func_name': list(functions_info['trigger_functions'].keys()),
}

# Dynamically add function-specific parameter ranges to the grid
for func_type, func_dict in [('filter', functions_info['filter_functions']),
                             ('setup', functions_info['setup_functions']),
                             ('trigger', functions_info['trigger_functions'])]:
    for func_name, func_info in func_dict.items():
        for param_name, (param_type, start, end) in func_info['params'].items():
            if param_type == 'int':
                param_grid[f'{func_type}_params__{param_name}'] = np.arange(start, end + 1)
            elif param_type == 'float':
                param_grid[f'{func_type}_params__{param_name}'] = np.linspace(start, end, num=10)


if __name__ == "__main__":
    # Fetch data for training
    df = fetch_data("Training")

    # Initialize the custom trading strategy
    strategy = TradingStrategy()

    # Define a custom scorer
    scorer = make_scorer(custom_scorer, greater_is_better=True)

    # Choose optimization strategy: RandomizedSearchCV
    search = RandomizedSearchCV(strategy, param_grid, n_iter=50, scoring=scorer, cv=3)  # Adjust n_iter for practicality

    # Perform the search
    search.fit(df)

    # Output the best parameters and score
    print("Best Parameters:", search.best_params_)
    print("Best Score:", search.best_score_)
