from django.conf.urls import include, url
from parlaposlanci.views import *


urlpatterns = [

    url(r'^getListOfMember/(?P<org_id>\d+)/(?P<date_>[\w].+)', getListOfMembersTickers),
    url(r'^getListOfMembers/(?P<org_id>\d+)', getListOfMembersTickers),

    url(r'^getCompass/(?P<org_id>\d+)/(?P<date_>[\w].+)', getCompass),
    url(r'^getCompass/(?P<org_id>\d+)', getCompass),
]
