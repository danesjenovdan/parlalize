from django.conf.urls import patterns, include, url
from parlaseje.views import *


urlpatterns = patterns(
	url(r'^getSpeech/(?P<speech_id>\d+)', getSpeech),
	url(r'^setAllSessions/', setAllSessions),
    url(r'^setMotionOfSession/(?P<id_se>\d+)', setMotionOfSession),
    url(r'^getMotionOfSession/(?P<id_se>\d+)', getMotionOfSession),
    url(r'^getMotionGraph/(?P<id_se>\d+)', getMotionGraph),
    url(r'^setAbsentMPs/(?P<id_se>\d+)', setAbsentMPs),
    url(r'^getAbsentMPs/(?P<id_se>\d+)', getAbsentMPs),
    url(r'^setPresenceOfPG/(?P<id_se>\d+)', setPresenceOfPG),
    url(r'^getPresenceOfPG/(?P<id_se>\d+)', getPresenceOfPG),
    url(r'^getPresenceOfPG/(?P<id_se>\d+)/(?P<date>[\w].+)', getPresenceOfPG),

)
