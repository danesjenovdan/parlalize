from django.conf.urls import include, url

from django.contrib import admin

from parlaseje.utils_ import getSessionDataAPI
from parlaskupine.utils_ import getPgDataAPI
from parlalize.utils_ import modelsData, getPersonsCardDates, getOrgsCardDates, getAllStaticData, monitorMe, recacheLastSession, getPersonDataAPI
from parlaposlanci.views import index

# admin.autodiscover()

urlpatterns = [
    url(r'^$', index),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^v1/p/', include('parlaposlanci.urls')),
    url(r'^v1/pg/', include('parlaskupine.urls')),
    url(r'^v1/s/', include('parlaseje.urls')),
    url(r'^v1/tasks/', include('utils.urls')),
    url(r'^v1/utils/getPersonData/(?P<id_parladata>\d+)/(?P<date_>[\w].+)', getPersonDataAPI),
    url(r'^v1/utils/getPersonData/(?P<id_parladata>\d+)', getPersonDataAPI),
    url(r'^v1/utils/getSessionData/(?P<session_id>\d+)', getSessionDataAPI),
    url(r'^v1/utils/getPgDataAPI/(?P<id_parladata>\d+)', getPgDataAPI),
    url(r'^v1/utils/getModelsData/', modelsData),
    url(r'^v1/utils/getPersonCardDates/(?P<person_id>\d+)', getPersonsCardDates),
    url(r'^v1/utils/getOrgsCardDates/(?P<org_id>\d+)', getOrgsCardDates),
    url(r'^v1/utils/getAllStaticData/', getAllStaticData),
    url(r'^v1/utils/recacheLastSession/', recacheLastSession),
    url(r'^v1/monitoring/', monitorMe),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),

    url(r'^v2/p/', include('parlaposlanci.urls_v2')),
    url(r'^v2/pg/', include('parlaskupine.urls_v2')),
    url(r'^v2/s/', include('parlaseje.urls_v2')),
]
