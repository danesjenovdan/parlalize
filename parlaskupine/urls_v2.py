from django.conf.urls import include, url
from django.conf import settings
from .views import *

from rest_framework import routers
from .api import TFIDFView

router = routers.DefaultRouter()
router.register(r'tfidfs', TFIDFView)


urlpatterns = [
    url(r'^getListOfPGs/(?P<organization_id>\d+)/(?P<date_>[\w].+)/', getListOfPGs),
    url(r'^getListOfPGs/(?P<organization_id>\d+)', getListOfPGs),
]
