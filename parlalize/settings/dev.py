# -*- coding: utf-8 -*-
from .defaults import *
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'hashhashhashhashashwkopaskfpjoivanijfdsf2332fdw'

# SECURITY WARNING: don't run with debug turned on in production!
DEVELOPMENT = True
DEBUG = DEVELOPMENT

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'localhost',
        'NAME': 'parlalize',
        'USER': 'parlauser',
        'PASSWORD': 'parlapassword',
    }
}

YES = ['yes']
NOT_PRESENT =  ['no']
AGAINST = ['against']
ABSTAIN = ['kvorum']

VOTE_MAP = {
    "aye": 1, # for
    "no": -1, # against
    "tellaye": 0, # abstain
    "tellno": 0, # not present
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

# static files for development
# STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# static files for production
STATIC_URL ='/parlastatic/parlalize/'
STATIC_ROOT = '/home/parlauser/parlastatic/parlalize/'

API_URL = "http://localhost:8000/v1"
ISCI_URL = "http://localhost:8888"
BASE_URL = 'http://localhost:8080/v1'
DASHBOARD_URL = 'http://localhost:8881'
SOLR_URL = 'http://127.0.0.1:8983/solr/parlameter'
FRONT_URL = 'http://parlameter.si'
NOTIFICATIONS_API = 'http://obvestila.parlameter.si'

GLEJ_URL = ''
PAGE_URL = ''

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

SETTER_KEY = "nekijabolteskega"

RAVEN_CONFIG = {
    #'dsn': 'http://123sdfsd123:123gdfsg123@sentry.url.si/40',
}

slack_token = 'sdfsdf-234234234-234234-234234-wer23rwerr2r23rwer23'

PARSER_UN = "parseruser"
PARSER_PASS = "parserpassword"

ALL_STATIC_CACHE_AGE = 48

if not DEVELOPMENT:
    FORCE_SCRIPT_NAME = '/analize'

DZ = 95
COUNCIL_ID = 9

PS_NP = ['pg', 'unaligned MP']
PS = 'pg'

HAS_LEGISLATIONS = True

