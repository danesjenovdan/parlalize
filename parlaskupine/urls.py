from django.conf.urls import patterns, include, url
from parlaskupine.views import *


urlpatterns = patterns('',
    # setters
    # TJ
    url(r'^setBasicInfOfPG/(?P<pg_id>\d+)', setBasicInfOfPG),
    url(r'^setPercentOFAttendedSessionPG/(?P<pg_id>\d+)', setPercentOFAttendedSessionPG),

    # TK
    url(r'^setMostMatchingThem/(?P<pg_id>\d+)/(?P<date>[\w].+)', setMostMatchingThem),
    url(r'^setMostMatchingThem/(?P<pg_id>\d+)', setMostMatchingThem),

    url(r'^setLessMatchingThem/(?P<pg_id>\d+)/(?P<date>[\w].+)', setLessMatchingThem),
    url(r'^setLessMatchingThem/(?P<pg_id>\d+)', setLessMatchingThem),

    url(r'^setDeviationInOrg/(?P<pg_id>\d+)/(?P<date>[\w].+)', setDeviationInOrg),
    url(r'^setDeviationInOrg/(?P<pg_id>\d+)', setDeviationInOrg),

    url(r'^setCutVotes/(?P<pg_id>\d+)/(?P<date>[\w].+)', setCutVotes),
    url(r'^setCutVotes/(?P<pg_id>\d+)', setCutVotes),


    # getters
    # TJ
    url(r'^getBasicInfOfPG/(?P<pg_id>\d+)', getBasicInfOfPG),
    url(r'^getPercentOFAttendedSessionPG/(?P<pg_id>\d+)', getPercentOFAttendedSessionPG),


    # TK
    url(r'^getMostMatchingThem/(?P<pg_id>\d+)/(?P<date>[\w].+)', getMostMatchingThem),
    url(r'^getMostMatchingThem/(?P<pg_id>\d+)/', getMostMatchingThem),

    url(r'^getLessMatchingThem/(?P<pg_id>\d+)/(?P<date>[\w].+)', getLessMatchingThem),
    url(r'^getLessMatchingThem/(?P<pg_id>\d+)/', getLessMatchingThem),

    url(r'^getDeviationInOrg/(?P<pg_id>\d+)/(?P<date>[\w].+)', getDeviationInOrg),
    url(r'^getDeviationInOrg/(?P<pg_id>\d+)/', getDeviationInOrg),

    url(r'^getCutVotes/(?P<pg_id>\d+)/(?P<date>[\w].+)', getCutVotes),
    url(r'^getCutVotes/(?P<pg_id>\d+)', getCutVotes),
)
