from django.conf.urls import include, url
from parlaposlanci.views import *


urlpatterns = [

    url(r'^getListOfMembersTickers/(?P<org_id>\d+)/(?P<date_>[\w].+)', getListOfMembersTickers),
    url(r'^getListOfMembersTickers/(?P<org_id>\d+)', getListOfMembersTickers),
]
