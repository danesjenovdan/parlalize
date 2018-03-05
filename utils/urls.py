from django.conf.urls import patterns, url
from .tasks import runAsyncSetter
from .legislations import test_legislation_statuses, check_for_legislation_final_vote


urlpatterns = patterns(
	'',
    url(r'^runner/$', runAsyncSetter),
    url(r'^testLegislationResults/$', test_legislation_statuses),
    url(r'^setLegislationsResults/$', check_for_legislation_final_vote),
    )