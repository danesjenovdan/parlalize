# -*- coding: UTF-8 -*-
from parlalize.utils import *
import requests
import json
from django.http import JsonResponse
from parlaskupine.models import *
from collections import Counter
from parlalize.settings import API_URL


# Create your views here.


def setBasicInfOfPG(request, pg_id):
    dic = dict()
    data = requests.get(API_URL+'/getBasicInfOfPG/'+str(pg_id)+'/').json()
#vprasi za shranjevanje yes and no
    result = saveOrAbort(model=PGStatic,
                         organization=Organization.objects.get(id_parladata=int(pg_id)),
                         headOfPG = Person.objects.get(id_parladata=int(data['HeadOfPG'])),
                         #viceOfPG = Person.objects.get(id_parladata = data['ViceOfPG']),
                         numberOfSeats=data['NumberOfSeats'],
                         #allVoters=data['AllVoters'] ,facebook=data['Facebook'],
                         # twitter=data['Twitter'],
                         #email=data['Mail']
                         )

    return JsonResponse({'alliswell': True})

def getBasicInfOfPG(request, pg_id, date=None):
    card = getPGCardModel(PGStatic, pg_id, date)

    data = {
           'organization':card.organization,
           'headOfPG':card.heafOfPG,
           'viceOfPG':card.viceOfPG,
           'numberOfSeats':card.numberOfSeats,
           'allVoters':card.allVoters,
           'facebook':card.facebook,
           'twitter':card.twitter,
           'email':card.email
           }

    return JsonResponse(data)

def setPercentOFAttendedSessionPG(request, pg_id):
   allSum = {}
   data = {}

   membersOfPG = requests.get(API_URL+'/getMembersOfPGs/').json()
   sessions =  requests.get(API_URL+'/getSessions/').json()
   data = {i:[requests.get(API_URL+'/getNumberOfMPAttendedSessions/'+str(mem)+'/').json() for mem in membersOfPG[i]] for i in membersOfPG}
   allSum = {i:(float(float(sum(data[i])) / (len(sessions)*len(data[i])))) * 100 for i in data}
   maximumPG = max(allSum.iterkeys(), key=(lambda key: allSum[key]))
   average = sum(allSum.values()) / len(allSum)
   maximum = allSum[maximumPG]

    #kaksen bo interfejs ko bo imela prav ta PG maksimum
   result = saveOrAbort(model=PercentOFAttendedSession,
                        organization=Organization.objects.get(id_parladata=int(pg_id)),
                        organization_value = allSum[pg_id],
                        maxPG=Organization.objects.get(id_parladata=maximumPG),
                        average=average,
                        maximum=maximum)

   return JsonResponse({'alliswell': True})

def getPercentOFAttendedSessionPG(requests, pg_id, date=None):

    card = getPGCardModel(PercentOFAttendedSession, pg_id, date)

 # uprasi ce isto kot pri personu razdelimo
    data = {
           'organization':card.organization,
           'organization_valuer':card.organization_value,
           'maxPG':card.maxPG,
           'average':card.average,
           'maximum':card.maximum,
           }

    return JsonResponse(data)