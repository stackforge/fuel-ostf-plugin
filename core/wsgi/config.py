server = {
    'host': '0.0.0.0',
    'port': '8777'
}

app = {
    'root': 'core.wsgi.controllers.root.RootController',
    'modules': ['core.wsgi'],
    'debug': False,
}

logging = {
    'loggers': {
        'root': {'level': 'INFO', 'handlers': ['console']},
        'adapter': {'level': 'DEBUG', 'handlers': ['console']},
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'formatters': {
        'simple': {
            'format': ('%(asctime)s %(levelname)-5.5s [%(name)s]'
                       '[%(threadName)s] %(message)s')
        }
    },
}


jenkins_url = 'http://172.18.214.29:8080'
