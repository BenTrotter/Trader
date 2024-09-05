from indicator_filter import *
from indicator_setup import *
from indicator_trigger import *

# Define available functions and their parameter ranges
functions_info = {

    # Filter Functions

    'filter_functions': {
        'generate_SMA_filter_signal': {
            'function': generate_SMA_filter_signal,
            'params': {
                'sma_window': ('int', 5, 15), 
                'look_back_period': ('int', 1, 5) 
            }
        },
        'generate_BollingerBands_filter_signal': {
            'function': generate_BollingerBands_filter_signal,
            'params': {
                'bollinger_window': ('int', 5, 20),
                'num_std_dev': ('float', 0.5, 2.5) 
            }
        }
    },

    # Set Up Functions

    'setup_functions': {
        'generate_RSI_setup_signal': {
            'function': generate_RSI_setup_signal,
            'params': {
                'period': ('int', 5, 20),
                'overbought_condition': ('int', 55, 70), 
                'oversold_condition': ('int', 30, 45) 
            }
        },
        'generate_Stochastic_setup_signal': {
            'function': generate_Stochastic_setup_signal,
            'params': {
                'k_period': ('int', 5, 15),  
                'd_period': ('int', 3, 7),  
                'stochastic_overbought': ('int', 55, 70),
                'stochastic_oversold': ('int', 30, 45)  
            }
        }
    },

    # Trigger Functions

    'trigger_functions': {
        'generate_MACD_trigger_signal': {
            'function': generate_MACD_trigger_signal,
            'params': {
                'fast_period': ('int', 1, 5), 
                'slow_period': ('int', 4, 10),  
                'signal_period': ('int', 1, 7)  
            }
        },
        'generate_MA_crossover_trigger_signal': {
            'function': generate_MA_crossover_trigger_signal,
            'params': {
                'short_window': ('int', 5, 15),  
                'long_window': ('int', 10, 25)  
            }
        }
    }
}