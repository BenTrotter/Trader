from indicator_filter import *
from indicator_setup import *
from indicator_trigger import *

# Define available functions and their parameter ranges
swing_functions_info = {

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
                'sma_window': ('int', 10, 50), # TODO: Add intervals for ML to search over
                'look_back_period': ('int', 1, 3) 
            }
        },
        'generate_BollingerBands_filter_signal': {
            'function': generate_BollingerBands_filter_signal,
            'params': {
                'bollinger_window': ('int', 15, 30),
                'num_std_dev': ('float', 1, 2) 
            }
        },
        'generate_ATR_filter_signal': {
            'function': generate_ATR_filter_signal,
            'params': {
                'filter_atr_window': ('int', 10, 30),
                'atr_upper_threshold': ('float', 30, 60),
                'atr_lower_threshold': ('float', 10, 25)
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
                'period': ('int', 10, 20),
                'overbought_condition': ('int', 65, 75), 
                'oversold_condition': ('int', 25, 40) 
            }
        },
        'generate_Stochastic_setup_signal': {
            'function': generate_Stochastic_setup_signal,
            'params': {
                'k_period': ('int', 10, 20),  
                'd_period': ('int', 3, 5),  
                'stochastic_overbought': ('int', 70, 80),
                'stochastic_oversold': ('int', 20, 35)  
            }
        },
        'generate_ADX_setup_signal': {
            'function': generate_ADX_setup_signal,
            'params': {
                'adx_window': ('int', 14, 28),
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
                'fast_period': ('int', 5, 12), 
                'slow_period': ('int', 20, 50),  
                'signal_period': ('int', 5, 12)  
            }
        },
        'generate_MA_crossover_trigger_signal': {
            'function': generate_MA_crossover_trigger_signal,
            'params': {
                'short_window': ('int', 10, 20),  
                'long_window': ('int', 30, 50)  
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