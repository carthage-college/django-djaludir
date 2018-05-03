"""
Django settings for project.
"""

import os

from djzbar.settings import INFORMIX_EARL_TEST as INFORMIX_EARL
#from djzbar.settings import INFORMIX_EARL_PROD as INFORMIX_EARL

# Debug
DEBUG = True
INFORMIX_DEBUG = ''
ADMINS = (
    ('', ''),
)
MANAGERS = ADMINS

SECRET_KEY = ''
ALLOWED_HOSTS =  ['localhost','127.0.0.1']
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Chicago'
SITE_ID = 1
USE_I18N = False
USE_L10N = False
USE_TZ = False
DEFAULT_CHARSET = 'utf-8'
FILE_CHARSET = 'utf-8'
SERVER_URL = ''
API_URL = "{}/{}".format(SERVER_URL, 'api')
LIVEWHALE_API_URL = "https://{}".format(SERVER_URL)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ROOT_DIR = os.path.dirname(__file__)
ROOT_URL = '/alumni/directory/'
ROOT_URLCONF = 'djaludir.core.urls'
WSGI_APPLICATION = 'djaludir.wsgi.application'
MEDIA_ROOT = ''
STATIC_ROOT = ''
STATIC_URL = '/static/djaludir/'
STATICFILES_DIRS = ()
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
DATABASES = {
    'default': {
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'NAME': 'django_djaludir',
        'ENGINE': 'django.db.backends.mysql',
        'USER': '',
        'PASSWORD': ''
    },
}
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'djaludir.core',
    'djaludir.registration',
    'djaludir.manager',
    'djtools',
)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(os.path.dirname(__file__), 'templates'),
            '/data2/django_templates/djkorra/',
            '/data2/django_templates/djcher/',
            '/data2/django_templates/',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug':DEBUG,
            'context_processors': [
                'djtools.context_processors.sitevars',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.messages.context_processors.messages',
            ],
            #'loaders': [
            #    # insert your TEMPLATE_LOADERS here
            #]
        },
    },
]
# caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        #'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        #'LOCATION': '127.0.0.1:11211',
        #'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        #'LOCATION': '/var/tmp/django_directory_cache',
        #'TIMEOUT': 60*20,
        #'KEY_PREFIX': "DJALUDIR_",
        #'OPTIONS': {
            #'MAX_ENTRIES': 80000,
        #}
    }
}
#CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True
#CACHE_MIDDLEWARE_SECONDS = 60*60*24*7
#CACHE_MIDDLEWARE_SECONDS = 60*20
#CACHE_MIDDLEWARE_KEY_PREFIX = "DJALUDIR_"
# SMTP settings
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_FAIL_SILENTLY = True
DEFAULT_FROM_EMAIL = ''
SERVER_EMAIL = ''
SERVER_MAIL = ''
# LDAP Constants
LDAP_SERVER_PWM = ''
LDAP_PORT_PWM = ''
LDAP_PROTOCOL_PWM = ''
LDAP_BASE_PWM = ''
LDAP_USER_PWM = ''
LDAP_PASS_PWM = ''
LDAP_SERVER = ''
LDAP_PORT = ''
LDAP_PROTOCOL = ''
LDAP_BASE = ''
LDAP_USER = ''
LDAP_PASS = ''
LDAP_EMAIL_DOMAIN = ''
LDAP_OBJECT_CLASS = ''
LDAP_OBJECT_CLASS_LIST = []
LDAP_GROUPS = {}
LDAP_RETURN = []
LDAP_RETURN_PWM = []
LDAP_ID_ATTR = ''
LDAP_CHALLENGE_ATTR = ''
LDAP_AUTH_USER_PK = False
LDAP_CREATE_TO_LIST = []
# auth backends
AUTHENTICATION_BACKENDS = (
    'djaludir.auth.backends.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)
LOGIN_URL = '/alumni/directory/auth/login/'
LOGOUT_URL = '/alumni/directory/auth/logout/'
LOGIN_REDIRECT_URL = '/alumni/directory/'
USE_X_FORWARDED_HOST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_DOMAIN = ''
SESSION_COOKIE_NAME = ''
SESSION_COOKIE_AGE = 86400
# App constants
MANAGER_RECIPIENTS = []
# Unit Tests
TEST_COLLEGE_ID = 0
# Hardcoded collection of relationships because the entire collection
# of values in rel_table are not valid for the alumni directory
RELATIONSHIPS = dict([
    ('',''),('HW1','Husband'),('HW2','Wife'),('PC1','Parent'),
    ('PC2','Child'),('SBSB','Sibling'),('COCO','Cousin'),
    ('GPGC1','Grandparent'),('GPGC2','Grandchild'),('AUNN1','Aunt/Uncle'),
    ('AUNN2','Niece/Nephew')
])
# logging
LOG_FILEPATH = os.path.join(os.path.dirname(__file__), 'logs/')
LOG_FILENAME = LOG_FILEPATH + 'debug.log'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format' : '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
            'datefmt' : '%Y/%b/%d %H:%M:%S'
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
            'datefmt' : '%Y/%b/%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'logfile': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILENAME,
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'include_html': True,
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'djaludir.registration': {
            'handlers':['logfile'],
            'propagate': True,
            'level':'DEBUG',
        },
        'djaludir.manager': {
            'handlers':['logfile'],
            'propagate': True,
            'level':'DEBUG',
        },
        'djauth': {
            'handlers':['logfile'],
            'propagate': True,
            'level':'DEBUG',
        }
        'django': {
            'handlers':['console'],
            'propagate': True,
            'level':'WARN',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
