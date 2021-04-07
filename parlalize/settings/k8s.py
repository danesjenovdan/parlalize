from .defaults import *
import dj_database_url

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'hashhashhashhashashwkopaskfpjoivanijfdsf2332fdw'

# SECURITY WARNING: don't run with debug turned on in production!
DEVELOPMENT = True
DEBUG = DEVELOPMENT

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'HOST': 'db',
#         'NAME': 'parlalize',
#         'USER': 'postgres',
#         'PASSWORD': 'postgres',
#     }
# }

DATABASES = {
    'default': dj_database_url.parse(os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3'), conn_max_age=600)
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
API_URL_V2 = "http://localhost:8000/v2"
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
UNALIGNED = 'unaligned MP'

WBS = ['committee',
       'comission',
       'investigative comission']

HAS_LEGISLATIONS = True

# Vote classificators. Vote text contains. This is tied to VOTE_NAMES.

# Vote classificators. Vote text contains. This is tied to VOTE_NAMES.
VOTE_INDICATORS = { 
    '1': ['dnevni red', 'širitev dnevnega reda', 'umik točke dnevnega reda'], 
    '2': ['glasovanje o zakonu v celoti'], 
    '3': ['amandma'], 
    '4': ['interpelacija'], 
    '5': ['evidenčni sklep'], 
    '6': ['predlog sklepa'], 
    '7': ['zakon o ratifikaciji'], 
    '8': ['sklep o imenovanju', 
          'predlog za imenovanje', 
          'izvolitev', 
          'soglasje k imenovanju', 
          'predlog kandidata', 
          'predlog kandidatke', 
          'sklep o izvolitvi', 
          'predlog za izvolitev'], 
    '9': ['predlog za razpis'], 
    '10': ['priporočilo'], 
    '11': ['poročilo'], 
    '12': ['proceduralni predlog'], 
    '13': ['odlok o načrtu ravnanja s stvarnim premoženjem'],
}

# Vote classification
VOTE_NAMES = { 
    '1': 'agenda', # agenda
    '2': 'whole_law', # final votiong 
    '3': 'amendment', # amendment
    '4': 'no_confidence', # interpelation
    '5': 'record_conclusion', # record conclusion
    '6': 'conclusion_proposal', # proposal for a decision
    '7': 'ratification', # ratification law
    '8': 'naming', # naming
    '9': 'call_proposal', # proposal for a call
    '10': 'recommendation', # recommendation 
    '11': 'report', # report 
    '12': 'procedural_proposal', # procedural proposal 
    '13': 'personal_property_decree',
    '14': 'other' # others
}

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SLACK_TOKEN = '123'
