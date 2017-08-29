from django.conf.urls import patterns, url
from .tasks import runAsyncSetter


urlpatterns = patterns(
	'',
    url(r'^runner/$', runAsyncSetter),
    )