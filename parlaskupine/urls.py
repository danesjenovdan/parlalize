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

    url(r'^setAtLeastMatchingThem/(?P<pg_id>\d+)/(?P<date>[\w].+)', setAtLeastMatchingThem),
    url(r'^setAtLeastMatchingThem/(?P<pg_id>\d+)', setAtLeastMatchingThem),


    # getters
    # TJ
    url(r'^getBasicInfOfPG/(?P<pg_id>\d+)', getBasicInfOfPG),
    url(r'^getPercentOFAttendedSessionPG/(?P<pg_id>\d+)', getPercentOFAttendedSessionPG),


    # TK
    url(r'^getMostMatchingThem/(?P<pg_id>\d+)/(?P<date>[\w].+)', getMostMatchingThem),
    url(r'^getMostMatchingThem/(?P<pg_id>\d+)/', getMostMatchingThem),

    url(r'^getLessMatchingThem/(?P<pg_id>\d+)/(?P<date>[\w].+)', getLessMatchingThem),
    url(r'^getLessMatchingThem/(?P<pg_id>\d+)/', getLessMatchingThem),
)
