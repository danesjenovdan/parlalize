"""
Django settings for parlalize project.

Generated by 'django-admin startproject' using Django 1.8.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

import raven

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'exkqi8xb2vnn4a*fyh@1y)z7*amz0!9p15ce9acqotf@y*wjn&'

# SECURITY WARNING: don't run with debug turned on in production!
DEVELOPMENT = False
DEBUG = DEVELOPMENT

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'taggit',
    'djgeojson',
    'leaflet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'parlaposlanci',
    'parlaskupine',
    'parlaseje',
    'django_extensions',
    'raven.contrib.django.raven_compat',
    'corsheaders',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'parlalize.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'parlalize.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases


if not DEVELOPMENT:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'HOST': '192.168.110.31',
            'NAME': 'parlalize',
            'USER': 'parladaddy',
            'PASSWORD': 'razvrat',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'HOST': 'localhost',
            'NAME': 'parlalize',
            'USER': 'parladaddy',
            'PASSWORD': 'razvrat',
        }
    }


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'sl-si'

TIME_ZONE = 'Europe/Ljubljana'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/home/parladaddy/parlalize/static/'


LAST_ACTIVITY_COUNT = 10


#PARLALIZE votes represent
VOTE_MAP = {
    "za": 1,
    "proti": -1,
    "kvorum": 0,
    "ni": 0,
    "ni_poslanec": 0
}

if DEVELOPMENT:
    API_URL = "http://localhost:8000/v1"
    ISCI_URL = "http://localhost:8888"

else:
    API_URL = "https://data.parlameter.si/v1"
    ISCI_URL = "https://isci.parlameter.si"

BASE_URL = 'https://analize.parlameter.si/v1'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

RAVEN_CONFIG = {
    # removed for dev MUKI SETTINGS
     'dsn': 'http://4e425a27eba144b8938f588f3a60662b:cf6ef8ba155b4d8da53ca4dea6cf074e@sentry.ilol.si/41' if not DEVELOPMENT else '',
    # If you are using git, you can also automatically configure the
    # release based on the git info.
#    'release': raven.fetch_git_sha(os.path.dirname(__file__)),
}

API_DATE_FORMAT = '%d.%m.%Y'

# CORS config
CORS_ORIGIN_ALLOW_ALL = True
API_OUT_DATE_FORMAT = '%-d. %-m. %Y'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

slack_token = 'xoxp-2166854968-16070161283-174340973622-b24bc3486a697e4675a7574f1f5bba92'

SETTER_KEY = "vednoboljsi112358"