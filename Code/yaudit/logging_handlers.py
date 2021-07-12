import os
import logging
import logging.config
from datetime import datetime
import copy

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'message_default': {
            'format': '%(asctime)s |  %(levelname)s |  | %(message)s'
        }
    },
    'handlers': {
        'console_handler': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'message_default'
        },
        'file_handler': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': f'logs/default_logger-{datetime.now()}_log.log',
            'formatter': 'message_default',
        },
    },
    'loggers': {
        'FileLogger': {
            'handlers': ['console_handler', 'file_handler'],
            'level': 'INFO',
            'propagate': False,
        },
        '': {
            'handlers': ['console_handler'],
            'level': 'ERROR',
            'propagate': False,
        }
    }
}


def define_bot_logger():
    path = f'logs/bots'
    os.makedirs(path, exist_ok=True)
    logging.config.dictConfig(get_bot_config())


def get_bot_config():
    logging_config = copy.deepcopy(LOGGING)
    filename = f'logs/bots/configuration_{os.getenv("YAUDIT_CONFIGURATION_ID", 0)}' \
               f'-topic_{os.getenv("YAUDIT_TOPIC_ID", 0)}' \
               f'-account_{os.getenv("YAUDIT_ACCOUNT_ID", 0)}' \
               f'-{datetime.now()}' \
               f'-log.log'
    logging_config['handlers']['file_handler']['filename'] = filename
    return logging_config
