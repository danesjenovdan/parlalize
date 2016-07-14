from django.conf.urls import patterns, include, url
from parlaseje.views import *


urlpatterns = patterns(
	url(r'^getSpeech/(?P<speech_id>\d+)', getSpeech),
	url(r'^setAllSessions/', setAllSessions),

    
    url(r'^setMotionOfSession/(?P<id_se>\d+)', setMotionOfSession),
    url(r'^setMotionOfSession/(?P<id_se>\d+)/(?P<date_>[\w].+)', setMotionOfSession),
    
    url(r'^getMotionOfSession/(?P<id_se>\d+)', getMotionOfSession),
    url(r'^getMotionOfSession/(?P<id_se>\d+)/(?P<date>[\w].+)', getMotionOfSession),
    
    url(r'^getMotionGraph/(?P<id_se>\d+)', getMotionGraph),

    url(r'^setAbsentMPs/(?P<id_se>\d+)', setAbsentMPs),
    
    url(r'^getAbsentMPs/(?P<id_se>\d+)', getAbsentMPs),
    url(r'^getAbsentMPs/(?P<id_se>\d+)/(?P<date>[\w].+)', getAbsentMPs),

    url(r'^setPresenceOfPG/(?P<id_se>\d+)/(?P<date_>[\w].+)', setPresenceOfPG),
    url(r'^setPresenceOfPG/(?P<id_se>\d+)', setPresenceOfPG),
    
    url(r'^getPresenceOfPG/(?P<id_se>\d+)', getPresenceOfPG),
    url(r'^getPresenceOfPG/(?P<id_se>\d+)/(?P<date>[\w].+)', getPresenceOfPG),

    url(r'^setSpeechesOnSession/(?P<date>[\w].+)', setSpeechesOnSession),
    url(r'^getMaxSpeechesOnSession/(?P<date>[\w].+)', getMaxSpeechesOnSession),
    url(r'^getMinSpeechesOnSession/(?P<date>[\w].+)', getMinSpeechesOnSession),

    url(r'^getMinSpeechesOnSession/', getMinSpeechesOnSession),
    url(r'^getMaxSpeechesOnSession/', getMaxSpeechesOnSession),

    #runenr
    url(r'^runSetters/(?P<date_to>[\w].+)', runSetters),
)
