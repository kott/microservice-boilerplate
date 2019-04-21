LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
        'json': {
            '()': '${LOG_FORMATTER_CLASS}',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'json',
            'stream': 'ext://sys.stdout',
        }
    },
    'loggers': {
        'werkzeug': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': 0,
        },
        'requests.packages.urllib3': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': 0,
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },
}


MAX_LOG_LENGTH = 32768
