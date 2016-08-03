from django.conf.urls import patterns, include, url

from django.contrib import admin

from utils import getPersonDataAPI

# admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^v1/p/', include('parlaposlanci.urls')),
    (r'^v1/pg/', include('parlaskupine.urls')),
    (r'^v1/s/', include('parlaseje.urls')),
    (r'^v1/utils/getPersonData/(?P<id_parladata>\d+)/(?P<date_>[\w].+)', getPersonDataAPI),
    (r'^v1/utils/getPersonData/(?P<id_parladata>\d+)', getPersonDataAPI),

)
