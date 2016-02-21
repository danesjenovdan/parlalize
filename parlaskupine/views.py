# -*- coding: UTF-8 -*-
from parlalize.utils import *
import requests
import json
from django.http import JsonResponse
from parlaskupine.models import *
from collections import Counter
from parlalize.settings import API_URL
import numpy as np
from scipy.stats.stats import pearsonr
from parlaposlanci.models import Person
from parlaposlanci.views import getMPsList
import math

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


def howMatchingThem(request, pg_id, type_of, date=None):
    r = requests.get(API_URL+'/getMembersOfPGs/')
    membersInPGs = r.json()
    if date:
        votes = getLogicVotes(date)
        date_of = datetime.strptime(date, '%d.%m.%Y')
    else:
        votes = getLogicVotes()
        date_of = datetime.now().date()
    pgVotes = {}

    # get average score of PG
    pg_score = np.mean([[votes[str(member)][b]
                       for b in sorted(votes[str(member)])]
                       for member in membersInPGs[str(pg_id)]],
                       axis=0)

    # most match them
    if type_of == "match":
        print "match"
        for voter in membersInPGs[str(pg_id)]:
            print voter
            votes.pop(str(voter))

    # deviation in PG
    if type_of == "deviation":
        del membersInPGs[str(pg_id)]
        for pgs in membersInPGs.keys():
            for voter in membersInPGs[str(pgs)]:
                print voter
                votes.pop(str(voter))


    members = getMPsList(request)
    membersDict = {str(mp['id']): mp for mp in json.loads(members.content)}

    out = {person: pearsonr(list(pg_score), [votes[str(person)][str(val)] for val in sorted(votes[str(person)])])[0] for person in sorted(votes.keys())}
    for person in out.keys():
        if math.isnan(out[person]):
            out.pop(person, None)

    keys = sorted(out, key=out.get)
    keys = sorted(out, key=out.get)

    for key in keys:
        membersDict[key].update({'ratio': out[str(key)]})
        membersDict[key].update({'id': key})
    return membersDict, keys, date_of


def setMostMatchingThem(request, pg_id, date=None):
    if date:
        members, keys, date_of = howMatchingThem(request, pg_id, date=date, type_of="match")
    else:
        members, keys, date_of = howMatchingThem(request, pg_id, type_of="match")

    out = {index: members[key] for key, index in zip(keys[-6:-1], [5, 4, 3, 2, 1])}

    result = saveOrAbortNew(model=MostMatchingThem,
                            created_for=date_of,
                            organization=Organization.objects.get(id_parladata=int(pg_id)),
                            person1=Person.objects.get(id_parladata=int(out[1]['id'])),
                            votes1=out[1]['ratio'],
                            person2=Person.objects.get(id_parladata=int(out[2]['id'])),
                            votes2=out[2]['ratio'],
                            person3=Person.objects.get(id_parladata=int(out[3]['id'])),
                            votes3=out[3]['ratio'],
                            person4=Person.objects.get(id_parladata=int(out[4]['id'])),
                            votes4=out[4]['ratio'],
                            person5=Person.objects.get(id_parladata=int(out[5]['id'])),
                            votes5=out[5]['ratio'])
    return JsonResponse({'alliswell': True})


def setLessMatchingThem(request, pg_id, date=None):
    if date:
        members, keys, date_of = howMatchingThem(request, pg_id, date=date, type_of="match")
    else:
        members, keys, date_of = howMatchingThem(request, pg_id, type_of="match")

    out = {index: members[key] for key, index in zip(keys[:5], [1, 2, 3, 4, 5])}

    result = saveOrAbortNew(model=LessMatchingThem,
                            created_for=date_of,
                            organization=Organization.objects.get(id_parladata=int(pg_id)),
                            person1=Person.objects.get(id_parladata=int(out[1]['id'])),
                            votes1=out[1]['ratio'],
                            person2=Person.objects.get(id_parladata=int(out[2]['id'])),
                            votes2=out[2]['ratio'],
                            person3=Person.objects.get(id_parladata=int(out[3]['id'])),
                            votes3=out[3]['ratio'],
                            person4=Person.objects.get(id_parladata=int(out[4]['id'])),
                            votes4=out[4]['ratio'],
                            person5=Person.objects.get(id_parladata=int(out[5]['id'])),
                            votes5=out[5]['ratio'])
    return JsonResponse({'alliswell': True})


def setDeviationInOrg(request, pg_id, date=None):
    if date:
        members, keys, date_of = howMatchingThem(request, pg_id, date=date, type_of="deviation")
    else:
        members, keys, date_of = howMatchingThem(request, pg_id, type_of="deviation")

    out = {index: members[key] for key, index in zip(keys[:1], [1])}
    out.update({index: members[key] for key, index in zip(keys[-1:], [2])})
    print out
    result = saveOrAbortNew(model=DeviationInOrganization,
                            created_for=date_of,
                            organization=Organization.objects.get(id_parladata=int(pg_id)),
                            person1=Person.objects.get(id_parladata=int(out[1]['id'])),
                            votes1=out[1]['ratio'],
                            person2=Person.objects.get(id_parladata=int(out[2]['id'])),
                            votes2=out[2]['ratio'])
    return JsonResponse({'alliswell': True})


def getMostMatchingThem(request, pg_id, date=None):
    mostMatching = getPGCardModelNew(MostMatchingThem, pg_id, date)
    out = {
        'organization': {
            'name': Organization.objects.get(id_parladata=int(pg_id)).name,
            'id': int(pg_id)
        },
        'results': [
            {
                "ratio": mostMatching.votes1,
                "id": mostMatching.person1.id_parladata,
                "name": mostMatching.person1.name,
                "party": requests.get(API_URL+'/getMPParty/' + str(mostMatching.person1.id_parladata)).json(),
            },
            {
                "ratio": mostMatching.votes2,
                "id": mostMatching.person2.id_parladata,
                "name": mostMatching.person2.name,
                "party": requests.get(API_URL+'/getMPParty/' + str(mostMatching.person2.id_parladata) + '/').json(),
            },
            {
                "ratio": mostMatching.votes3,
                "id": mostMatching.person3.id_parladata,
                "name": mostMatching.person3.name,
                "party": requests.get(API_URL+'/getMPParty/' + str(mostMatching.person3.id_parladata) + '/').json(),
            },
            {
                "ratio": mostMatching.votes4,
                "id": mostMatching.person4.id_parladata,
                "name": mostMatching.person4.name,
                "party": requests.get(API_URL+'/getMPParty/' + str(mostMatching.person4.id_parladata) + '/').json(),
            },
            {
                "ratio": mostMatching.votes5,
                "id": mostMatching.person5.id_parladata,
                "name": mostMatching.person5.name,
                "party": requests.get(API_URL+'/getMPParty/' + str(mostMatching.person5.id_parladata) + '/').json(),
            }
        ]
    }

    return JsonResponse(out, safe=False)


def getLessMatchingThem(request, pg_id, date=None):
    mostMatching = getPGCardModelNew(LessMatchingThem, pg_id, date)
    out = {
        'organization': {
            'name': Organization.objects.get(id_parladata=int(pg_id)).name,
            'id': int(pg_id)
        },
        'results': [
            {
                "ratio": mostMatching.votes1,
                "id": mostMatching.person1.id_parladata,
                "name": mostMatching.person1.name,
                "party": requests.get(API_URL+'/getMPParty/' + str(mostMatching.person1.id_parladata)).json(),
            },
            {
                "ratio": mostMatching.votes2,
                "id": mostMatching.person2.id_parladata,
                "name": mostMatching.person2.name,
                "party": requests.get(API_URL+'/getMPParty/' + str(mostMatching.person2.id_parladata) + '/').json(),
            },
            {
                "ratio": mostMatching.votes3,
                "id": mostMatching.person3.id_parladata,
                "name": mostMatching.person3.name,
                "party": requests.get(API_URL+'/getMPParty/' + str(mostMatching.person3.id_parladata) + '/').json(),
            },
            {
                "ratio": mostMatching.votes4,
                "id": mostMatching.person4.id_parladata,
                "name": mostMatching.person4.name,
                "party": requests.get(API_URL+'/getMPParty/' + str(mostMatching.person4.id_parladata) + '/').json(),
            },
            {
                "ratio": mostMatching.votes5,
                "id": mostMatching.person5.id_parladata,
                "name": mostMatching.person5.name,
                "party": requests.get(API_URL+'/getMPParty/' + str(mostMatching.person5.id_parladata) + '/').json(),
            }
        ]
    }

    return JsonResponse(out, safe=False)


def getDeviationInOrg(request, pg_id, date=None):
    mostMatching = getPGCardModelNew(DeviationInOrganization, pg_id, date)
    out = {
        'organization': {
            'name': Organization.objects.get(id_parladata=int(pg_id)).name,
            'id': int(pg_id)
        },
        'results': [
            {
                "ratio": mostMatching.votes1,
                "id": mostMatching.person1.id_parladata,
                "name": mostMatching.person1.name,
                "party": requests.get(API_URL+'/getMPParty/' + str(mostMatching.person1.id_parladata)).json(),
            },
            {
                "ratio": mostMatching.votes2,
                "id": mostMatching.person2.id_parladata,
                "name": mostMatching.person2.name,
                "party": requests.get(API_URL+'/getMPParty/' + str(mostMatching.person2.id_parladata) + '/').json(),
            },
        ]
    }
    return JsonResponse(out, safe=False)
