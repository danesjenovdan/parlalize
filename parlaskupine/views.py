# -*- coding: UTF-8 -*-
from parlalize.utils import *
import requests
import json
from django.http import JsonResponse
from parlaskupine.models import *
from parlaseje.models import Activity,Session
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

def getPercentOFAttendedSessionPG(request, pg_id, date=None):

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

def setMPsOfPG(request, pg_id):
    result ={}
    results = []
    membersOfPG = requests.get(API_URL+'/getMembersOfPGs/').json()
    for mOfPg in membersOfPG[pg_id]:
      results.append(mOfPg)

    result = saveOrAbort(model=MPOfPg,
                        id_parladata=pg_id,
                        MPs =  results
                        )
 
    return JsonResponse({'alliswell': True})

#shranjevaje se naredi
def getMPsOfPG(request, pg_id):
    mps = requests.get(API_URL+'/getMPs/').json()
    result ={}
    results = {}
    ids = MPOfPg.objects.get(id_parladata=int(pg_id)).MPs
    print ids
    for MP in ids:
        for mp in mps:
            if str(mp['id']) == str(MP):
                result = {'name':mp['name'], 'image':mp['image']}
                results[mp['id']] = result
    return JsonResponse(results, safe=False)


def getSpeechesOfPG(request, pg_id, date=False):
  if date:
    allSessions = Session.objects.filter(start_time__lte=datetime.strptime(date, '%d.%m.%Y'))
  else:
    allSessions = Session.objects.all()
  results = list()
  mp = dict()
  speec = list()

  for session in allSessions:
    if Activity.objects.filter(session_id=session.id):
      allSpeeches = Speech.objects.filter(session_id=session.id, organization = pg_id)
      for speech in allSpeeches:
        if speech.person_id in mp:
          mp[speech.person_id]['speech'].append(speech.id)
        else:
          mp.update({speech.person_id:{'name':Person.objects.get(id=speech.person_id).name,'image':Person.objects.get(id=speech.person_id).image, 'speech':list([speech.id])}})
      results.append({'session':session.name,'time':session.start_time, 'mps':mp})
      mp={}
      speec = []
  return JsonResponse(results, safe=False)
 #cutVotes
 #getSpeechesOfMP