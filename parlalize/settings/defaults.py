# -*- coding: utf-8 -*-
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
import sys

import raven
from django.utils.translation import gettext as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'taggit',
    'djgeojson',
    'leaflet',
    'dal',
    'dal_select2',
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
    'tinymce',
    'utils',
    'oauth2_provider',
    'rest_framework',
    'django_filters',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

WSGI_APPLICATION = 'parlalize.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'sl-si'

TIME_ZONE = 'Europe/Ljubljana'

USE_I18N = True

USE_L10N = True

USE_TZ = False


LAST_ACTIVITY_COUNT = 10


# PARLALIZE vote options represent for vote analyses
# in ballots we save the option as string. this is used to transform it to a numerical value

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


API_DATE_FORMAT = '%d.%m.%Y'
API_OUT_DATE_FORMAT = '%-d. %-m. %Y'
if sys.platform == 'win32':
    API_OUT_DATE_FORMAT = '%#d. %#m. %Y'

# CORS config
CORS_ORIGIN_ALLOW_ALL = True

# Legislation status options: in procedure / procedure ended
# we use these in the django admin interface to define select dropdown options
# it is tied to the model, so if you change this please check parlaseje.models.Legislation
# LEGISLATION_STATUS = [('under_consideration', _('v obravnavi')), ('end_of_hearing', _('konec obravnave'))]
LEGISLATION_STATUS = [
    ('enacted', 'enacted'),
    ('submitted', 'submitted'),
    ('rejected', 'rejected'),
    ('retracted', 'retracted'),
    ('adopted', 'adopted'),
    ('received', 'received'),
    ('in_procedure', 'in_procedure')
]
# Legislation result: empty / accepted / rejected
# we use these in the django admin interface to define select dropdown options
# it is tied to the model, so if you change this please check parlaseje.models.Legislation

# LEGISLATION_RESULT = [(None, _('Prazno')), ('accepted', _('sprejet')), ('rejected', _('zavrnjen'))]
LEGISLATION_RESULT = [
    ('enacted', 'enacted'),
    ('submitted', 'submitted'),
    ('rejected', 'rejected'),
    ('retracted', 'retracted'),
    ('adopted', 'adopted'),
    ('received', 'received'),
    ('in_procedure', 'in_procedure')
]

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

TINYMCE_INCLUDE_JQUERY = False

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAdminUser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    #'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
}

OAUTH2_PROVIDER = {
    'OAUTH2_BACKEND_CLASS': 'oauth2_provider.oauth2_backends.JSONOAuthLibCore'
}
