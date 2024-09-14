from indicator_filter import *
from indicator_setup import *
from indicator_trigger import *

# Define available functions and their parameter ranges
intra_functions_info = {

    # Filter Functions
    
    'filter_functions': {
        'noop_filter': {
            'function': noop_filter,
            'params': {

            }
        },
        'generate_SMA_filter_signal': {
            'function': generate_SMA_filter_signal,
            'params': {
                'sma_window': ('int', 5, 15), # TODO: Add intervals for ML to search over
                'look_back_period': ('int', 1, 5) 
            }
        },
        'generate_BollingerBands_filter_signal': {
            'function': generate_BollingerBands_filter_signal,
            'params': {
                'bollinger_window': ('int', 5, 20),
                'num_std_dev': ('float', 0.5, 2.5) 
            }
        },
        'generate_ATR_filter_signal': {
            'function': generate_ATR_filter_signal,
            'params': {
                'filter_atr_window': ('int', 5, 20),
                'atr_upper_threshold': ('float', 25, 40),
                'atr_lower_threshold': ('float', 5, 20)
            }
        }
    },

    # Set Up Functions

    'setup_functions': {
        'noop_setup': {
            'function': noop_setup,
            'params': {

            }
        },
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
        },
        'generate_ADX_setup_signal': {
            'function': generate_ADX_setup_signal,
            'params': {
                'adx_window': ('int', 7, 28),
                'strong_trend_threshold': ('int', 20, 35)
            }
        }
    },

    # Trigger Functions

    'trigger_functions': {
        'noop_trigger': {
            'function': noop_trigger,
            'params': {

            }
        },
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
        },
        'generate_parabolic_sar_trigger_signal': {
            'function': generate_parabolic_sar_trigger_signal,
            'params': {
                'initial_af': ('int', 0.01, 0.05),  
                'max_af': ('int', 0.1, 0.3),
                'step_af': ('int', 0.01, 0.05)  
            }
        }
    }
}