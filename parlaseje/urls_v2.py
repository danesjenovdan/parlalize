from django.conf.urls import include, url
from parlaseje.views import *


urlpatterns = [
    url(r'^getLastSessionLanding/(?P<org_id>\d+)(/(?P<date_>[\w].+))?', getLastSessionLanding),
]
