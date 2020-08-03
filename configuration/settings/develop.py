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

INTERNAL_IPS = ['*']

RUNSERVERPLUS_SERVER_ADDRESS_PORT = '0.0.0.0:8080'


# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = '9gen&o^m2-dj&_nnmlcuwtnde(11bb+9+c+0-!-xf$q#0fu*!3'


# MAIL SETTINGS
# ------------------------------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = str(ROOT_DIR.path('sent_emails'))


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
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(str(ROOT_DIR), 'local.sqlite3'),
    }
}


# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
MEDIA_ROOT = '/home/user/'


# MAIL SETTINGS
# ------------------------------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = str(ROOT_DIR.path('sent_emails'))


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
            'filename': str(ROOT_DIR) + '/debug.log',
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