from django.conf.urls import url
from .tasks import runAsyncSetter, get_celery_status
from .legislations import test_legislation_statuses, check_for_legislation_final_vote


urlpatterns = [
    url(r'^runner/$', runAsyncSetter),
    url(r'^testLegislationResults/$', test_legislation_statuses),
    url(r'^setLegislationsResults/$', check_for_legislation_final_vote),
    url(r'^status/$', get_celery_status),
    ]