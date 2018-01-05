from django.conf.urls import patterns, url
from .tasks import runAsyncSetter
from .legislations import test_legislation_statuses


urlpatterns = patterns(
	'',
    url(r'^runner/$', runAsyncSetter),
    url(r'^testLegislationResults/$', test_legislation_statuses),
    )