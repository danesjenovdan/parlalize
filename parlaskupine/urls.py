from django.conf.urls import patterns, include, url
from parlaskupine.views import *


urlpatterns = patterns('',
#	url(r'^getMPsList/', getMPsList),
	url(r'^setBasicInfOfPG/(?P<pg_id>\d+)', setBasicInfOfPG),
    url(r'^getBasicInfOfPG/(?P<pg_id>\d+)', getBasicInfOfPG),
    url(r'^setPercentOFAttendedSessionPG/(?P<pg_id>\d+)', setPercentOFAttendedSessionPG),
    url(r'^getPercentOFAttendedSessionPG/(?P<pg_id>\d+)', getPercentOFAttendedSessionPG),
    url(r'^setMPsOfPG/(?P<pg_id>\d+)', setMPsOfPG),
    url(r'^getMPsOfPG/(?P<pg_id>\d+)', getMPsOfPG),

    url(r'^getSpeechesOfPG/(?P<pg_id>\d+)/(?P<date>[\w].+)', getSpeechesOfPG),
    url(r'^getSpeechesOfPG/(?P<pg_id>\d+)', getSpeechesOfPG),


)
