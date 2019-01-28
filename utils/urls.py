from django.conf.urls import url
from .legislations import test_legislation_statuses, check_for_legislation_final_vote


urlpatterns = [
    url(r'^testLegislationResults/$', test_legislation_statuses),
    url(r'^setLegislationsResults/$', check_for_legislation_final_vote),
    ]