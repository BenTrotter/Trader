from indicator_filter import *
from indicator_setup import *
from indicator_trigger import *

# Define available functions and their parameter ranges
functions_info = {
    'filter_functions': {
        'generate_SMA_filter_signal': {
            'function': generate_SMA_filter_signal,
            'params': {
                'sma_window': ('int', 50, 50),  # Adjusted range
                'look_back_period': ('int', 3, 3)  # Adjusted range
            }
        }
    },
    'setup_functions': {
        'generate_RSI_setup_signal': {
            'function': generate_RSI_setup_signal,
            'params': {
                'period': ('int', 14, 14),  # Adjusted range
                'overbought_condition': ('int', 70, 70),  # Adjusted range
                'oversold_condition': ('int', 30, 30)  # Adjusted range
            }
        }
    },
    'trigger_functions': {
        'generate_MACD_trigger_signal': {
            'function': generate_MACD_trigger_signal,
            'params': {
                'fast_period': ('int', 1, 1),  # Adjusted range
                'slow_period': ('int', 2, 2),  # Adjusted range
                'signal_period': ('int', 20, 20)  # Adjusted range
            }
        }
    }
}

