"""
Local settings for the project.

- Run in Debug mode
- Add django-extensions as app
- Add Django Debug Toolbar
- Add corsheaders as app
"""
import os
from .base import *  # noqa
from envparse import env


# DEBUG
# ------------------------------------------------------------------------------
DEBUG = True
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG


# SITE CONFIGURATION
# ------------------------------------------------------------------------------
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['*'])

INTERNAL_IPS = ['127.0.0.1', '10.60.3.4', '10.90.0.165']

RUNSERVERPLUS_SERVER_ADDRESS_PORT = '0.0.0.0:8080'


# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = '9gen&o^m2-dj&_nnmlcuwtnde(11bb+9+c+0-!-xf$q#0fu*!3'


# Mail settings
# ------------------------------------------------------------------------------
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 587
EMAIL_USE_TLS = True


# CACHING
# ------------------------------------------------------------------------------
CACHES = {
	'default': {
		'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
		'LOCATION': ''
	}
}


# django-debug-toolbar
# ------------------------------------------------------------------------------
MIDDLEWARE += [
	'debug_toolbar.middleware.DebugToolbarMiddleware',
]

DEBUG_TOOLBAR_CONFIG = {
	'DISABLE_PANELS': [
		'debug_toolbar.panels.redirects.RedirectsPanel',
	],
	'SHOW_TEMPLATE_CONTEXT': True,
}


# thrid-party-apps
# ------------------------------------------------------------------------------
INSTALLED_APPS += [
    'django_extensions',
    'debug_toolbar',
    'corsheaders',
]


# django-corsheaders
# ------------------------------------------------------------------------------
MIDDLEWARE += [
    'corsheaders.middleware.CorsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True

from corsheaders.defaults import default_headers
CORS_ALLOW_HEADERS = list(default_headers) + [
    'content-disposition'
]


# DATABASES
# ------------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST'),
        'PORT': '3306',
    }
}


# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
MEDIA_ROOT = '/home/user/'


# LOGGING
# ------------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/home/user/indo-medical-analysis-backend/debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'propagate': True,
            'level': 'INFO',
        },
        'werkzeug': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}