from operator import itemgetter
from .models import Organization, IntraDisunion
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

def getDisunionInOrgHelper(pg_id, date_of):
    ids = IntraDisunion.objects.filter(organization__id_parladata=pg_id,
                                       vote__start_time__lte=date_of)
    el = ids.values_list('maximum', flat=True)
    if len(el) != 0:
        suma = sum(map(float, el))/el.count()
    else:
        suma = 0

    return suma, ids


def getAmendmentsCount(pg_id, date_of):
    org = Organization.objects.get(id_parladata=pg_id)
    card = org.amendments.filter(start_time__lte=date_of)
    count = card.count()
    return org, count, card.latest('created_for').created_for