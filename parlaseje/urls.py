from django.conf.urls import patterns, include, url
from parlaseje.views import *


urlpatterns = patterns(
	url(r'^getSpeech/(?P<speech_id>\d+)', getSpeech),
	url(r'^setAllSessions/', setAllSessions),
)
