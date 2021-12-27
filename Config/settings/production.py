from decouple import Csv

from .base import *
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', cast=int),
        'ATOMIC_REQUESTS': True,
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = config('STATIC_ROOT')

MEDIA_URL = '/media/'
MEDIA_ROOT = config('MEDIA_ROOT')

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': config('CACHE_LOCATION'),
#     }
# }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'logfile': {
            'level': 'ERROR',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'logs/server.log',
            'when': 'D',
            'interval': 1,
            'backupCount': 30,
        },

    },
    'loggers': {
        'django': {
            'handlers': ['logfile']
        },
    },
}
