from .views import howMatchingThem
from operator import itemgetter
from .models import Organization
from datetime import datetime
from parlalize.settings import API_DATE_FORMAT
from django.http import JsonResponse

def cus():
	a = howMatchingThem(None, 5, "deviation")
	c=[{"ratio":a[0][g]["ratio"], "name": a[0][g]["name"]} for g in a[0] if "ratio" in a[0][g].keys()]
	from operator import itemgetter
	c = sorted(c, key=itemgetter('ratio'))
	return c


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
