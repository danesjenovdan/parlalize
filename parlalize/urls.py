from django.conf.urls import patterns, include, url

from django.contrib import admin

from parlaseje.utils import getSessionDataAPI
from parlaskupine.utils_ import getPgDataAPI
from parlalize.utils_ import modelsData, getPersonsCardDates, getOrgsCardDates, getAllStaticData, monitorMe, recacheLastSession, getPersonDataAPI
from utils.legislations import test_legislation_statuses

# admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^v1/p/', include('parlaposlanci.urls')),
    (r'^v1/pg/', include('parlaskupine.urls')),
    (r'^v1/s/', include('parlaseje.urls')),
    (r'^v1/tasks/', include('utils.urls')),
    (r'^v1/utils/getPersonData/(?P<id_parladata>\d+)/(?P<date_>[\w].+)', getPersonDataAPI),
    (r'^v1/utils/getPersonData/(?P<id_parladata>\d+)', getPersonDataAPI),
    (r'^v1/utils/getSessionData/(?P<session_id>\d+)', getSessionDataAPI),
    (r'^v1/utils/getPgDataAPI/(?P<id_parladata>\d+)', getPgDataAPI),
    (r'^v1/utils/getModelsData/', modelsData),
    (r'^v1/utils/getPersonCardDates/(?P<person_id>\d+)', getPersonsCardDates),
    (r'^v1/utils/getOrgsCardDates/(?P<org_id>\d+)', getOrgsCardDates),
    (r'^v1/utils/getAllStaticData/', getAllStaticData),
    (r'^v1/utils/recacheLastSession/', recacheLastSession),
    (r'^v1/utils/testLegislationResults/', test_legislation_statuses),
    (r'^v1/monitoring/', monitorMe),
    (r'^tinymce/', include('tinymce.urls')),
)
