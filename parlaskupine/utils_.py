from operator import itemgetter
from .models import Organization
from datetime import datetime
from parlalize.settings import API_DATE_FORMAT
from django.http import JsonResponse


def getPgDataAPI(request, id_parladata, date_=None):
    if not date_:
        date_ = datetime.now().strftime(API_DATE_FORMAT)
    org = Organization.objects.filter(id_parladata=id_parladata)
    if org:
    	return JsonResponse(org[0].getOrganizationData())
    else:
    	return JsonResponse({
                  'id': id_parladata,
                  'name': "unknown",
                  'acronym': "unknown",
               })
