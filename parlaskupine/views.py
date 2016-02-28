# -*- coding: UTF-8 -*-
from parlalize.utils import *
import requests
import json
from django.http import JsonResponse
from parlaskupine.models import *
from collections import Counter
from parlalize.settings import API_URL, API_DATE_FORMAT, BASE_URL
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
        date_of = datetime.strptime(date, API_DATE_FORMAT)
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
    try:
        out = {person: pearsonr(list(pg_score), [votes[str(person)][str(val)] for val in sorted(votes[str(person)])])[0] for person in sorted(votes.keys())}
    except:
        out = {}
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
    print out
    try:
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
    except:
        return JsonResponse({'alliswell': False})


def setLessMatchingThem(request, pg_id, date=None):
    if date:
        members, keys, date_of = howMatchingThem(request, pg_id, date=date, type_of="match")
    else:
        members, keys, date_of = howMatchingThem(request, pg_id, type_of="match")

    out = {index: members[key] for key, index in zip(keys[:5], [1, 2, 3, 4, 5])}
    try:
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
    except:
        return JsonResponse({'alliswell': False})


def setDeviationInOrg(request, pg_id, date=None):
    if date:
        members, keys, date_of = howMatchingThem(request, pg_id, date=date, type_of="deviation")
    else:
        members, keys, date_of = howMatchingThem(request, pg_id, type_of="deviation")

    out = {index: members[key] for key, index in zip(keys[:1], [1])}
    out.update({index: members[key] for key, index in zip(keys[-1:], [2])})
    try:
        result = saveOrAbortNew(model=DeviationInOrganization,
                                created_for=date_of,
                                organization=Organization.objects.get(id_parladata=int(pg_id)),
                                person1=Person.objects.get(id_parladata=int(out[1]['id'])),
                                votes1=out[1]['ratio'],
                                person2=Person.objects.get(id_parladata=int(out[2]['id'])),
                                votes2=out[2]['ratio'])
        return JsonResponse({'alliswell': True})
    except:
        return JsonResponse({'alliswell': False})


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


def setCutVotes(request, pg_id, date=None):
    def getMaxOrgData(data, ids):
        d = {str(pg): data[pg] for pg in ids}
        return ",".join([key for key,val in d.iteritems() if val == max(d.values())])

    r = requests.get(API_URL+'/getMembersOfPGs/')
    membersInPGs = r.json()

    if date:
        r = requests.get(API_URL+'/getVotes/' + date)
        date_of = datetime.strptime(date, API_DATE_FORMAT)
    else:
        r = requests.get(API_URL+'/getVotes/')
        date_of = datetime.now().date()
    votes = r.json()

    r = requests.get(API_URL+'/getCoalitionPGs/')
    coalition = r.json()

    pgs_for = {}
    pgs_against = {}
    pgs_abstain = {}
    pgs_absent = {}
    pgs_abstain = {}
    pgs_absent = {}

    coal_avg = {}
    oppo_avg = {}

    coal_pgs = [str(pg) for pg in coalition["coalition"]]
    oppo_pgs = [str(pg) for pg in coalition["opposition"]]

    votes_count = len(Vote.objects.all())
    tempVotesCoal = {"votes": [], "count": 0}
    tempVotesOppo = {"votes": [], "count": 0}
    # votes for
    for pg in membersInPGs:
        # in pg
        try:
            pgs_for[str(pg)] = normalize(sum(map(voteFor, [votes[str(member)][b]
                                         for member in membersInPGs[str(pg)] for b in sorted(votes[str(member)])]))/len(membersInPGs[str(pg)]), votes_count)
        except:
            pgs_for[str(pg)] = 0

        # average
        if pg in map(str, coalition["coalition"]):
            tempVotesCoal["votes"].extend([votes[str(member)][b]
                                           for member in membersInPGs[str(pg)]
                                           for b in sorted(votes[str(member)])])
            tempVotesCoal["count"] += len(membersInPGs[str(pg)])
        else:
            tempVotesOppo["votes"].extend([votes[str(member)][b]
                                           for member in membersInPGs[str(pg)]
                                           for b in sorted(votes[str(member)])])
            tempVotesOppo["count"] += len(membersInPGs[str(pg)])

    # Calculate coalition and opposition average
    coal_avg["for"] = normalize(sum(map(voteFor, tempVotesCoal["votes"]))/tempVotesCoal["count"], votes_count)
    oppo_avg["for"] = normalize(sum(map(voteFor, tempVotesOppo["votes"]))/tempVotesOppo["count"], votes_count)
    coal_avg["against"] = normalize(sum(map(voteAgainst, tempVotesCoal["votes"]))/tempVotesCoal["count"], votes_count)
    oppo_avg["against"] = normalize(sum(map(voteAgainst, tempVotesOppo["votes"]))/tempVotesOppo["count"], votes_count)
    coal_avg["abstain"] = normalize(float(sum(map(voteAbstain, tempVotesCoal["votes"])))/float(tempVotesCoal["count"]), votes_count)
    oppo_avg["abstain"] = normalize(sum(map(voteAbstain, tempVotesOppo["votes"]))/tempVotesOppo["count"], votes_count)
    coal_avg["absent"] = normalize(sum(map(voteAbsent, tempVotesCoal["votes"]))/tempVotesCoal["count"], votes_count)
    oppo_avg["absent"] = normalize(sum(map(voteAbsent, tempVotesOppo["votes"]))/tempVotesOppo["count"], votes_count)

    # get votes against
    for pg in membersInPGs:
        # in PGs
        try:
            pgs_against[str(pg)] = normalize(sum(map(voteAgainst, [votes[str(member)][b]
                                             for member in membersInPGs[str(pg)] for b in sorted(votes[str(member)])]))/len(membersInPGs[str(pg)]), votes_count)
        except:
            pgs_against[str(pg)] = 0


    # get votes abstain of PGs
    for pg in membersInPGs:
        try:
            pgs_abstain[str(pg)] = normalize(sum(map(voteAbstain, [votes[str(member)][b]
                                             for member in membersInPGs[str(pg)] for b in sorted(votes[str(member)])]))/len(membersInPGs[str(pg)]), votes_count)
        except:
            pgs_abstain[str(pg)] = 0

    # get votes obsent of PGs
    for pg in membersInPGs:
        try:
            pgs_absent[str(pg)] = normalize(sum(map(voteAbsent, [votes[str(member)][b]
                                            for member in membersInPGs[str(pg)] for b in sorted(votes[str(member)])]))/len(membersInPGs[str(pg)]), votes_count)
        except:
            pgs_absent[str(pg)] = 0

    final_response = saveOrAbortNew(
        CutVotes,
        created_for=date_of,
        organization=Organization.objects.get(id_parladata=pg_id),
        this_for=pgs_for[pg_id],
        this_against=pgs_against[pg_id],
        this_abstain=pgs_abstain[pg_id],
        this_absent=pgs_absent[pg_id],
        coalition_for=coal_avg["for"],
        coalition_against=coal_avg["against"],
        coalition_abstain=coal_avg["abstain"],
        coalition_absent=coal_avg["absent"],
        coalition_for_max=max([pgs_for[pg] for pg in coal_pgs]),
        coalition_against_max=max([pgs_against[pg] for pg in coal_pgs]),
        coalition_abstain_max=max([pgs_abstain[pg] for pg in coal_pgs]),
        coalition_absent_max=max([pgs_absent[pg] for pg in coal_pgs]),
        coalition_for_max_org=getMaxOrgData(pgs_for, coal_pgs),
        coalition_against_max_org=getMaxOrgData(pgs_against, coal_pgs),
        coalition_abstain_max_org=getMaxOrgData(pgs_abstain, coal_pgs),
        coalition_absent_max_org=getMaxOrgData(pgs_absent, coal_pgs),
        opposition_for=oppo_avg["for"],
        opposition_against=oppo_avg["against"],
        opposition_abstain=oppo_avg["abstain"],
        opposition_absent=oppo_avg["absent"],
        opposition_for_max=max([pgs_for[pg] for pg in oppo_pgs]),
        opposition_against_max=max([pgs_against[pg] for pg in oppo_pgs]),
        opposition_abstain_max=max([pgs_abstain[pg] for pg in oppo_pgs]),
        opposition_absent_max=max([pgs_absent[pg] for pg in oppo_pgs]),
        opposition_for_max_org=getMaxOrgData(pgs_for, oppo_pgs),
        opposition_against_max_org=getMaxOrgData(pgs_against, oppo_pgs),
        opposition_abstain_max_org=getMaxOrgData(pgs_abstain, oppo_pgs),
        opposition_absent_max_org=getMaxOrgData(pgs_absent, oppo_pgs)
    )

    return JsonResponse({'alliswell': True})


def getCutVotes(request, pg_id, date=None):
    cutVotes = getPGCardModelNew(CutVotes, pg_id, date)

    out = {
        'organization': {
            'id': int(pg_id),
            'name': Organization.objects.get(id_parladata=int(pg_id)).name
        },
        'results': {
            'abstain': {
                'score': cutVotes.this_abstain,
                'maxCoalition': {
                    'mps': [{'name': org.name, 'id': org.id_parladata} for org in Organization.objects.filter(id_parladata__in=[int(textid) for textid in cutVotes.coalition_abstain_max_org.split(',')])],
                    'score': cutVotes.coalition_abstain_max
                },
                'maxOpposition': {
                    'mps': [{'name': org.name, 'id': org.id_parladata} for org in Organization.objects.filter(id_parladata__in=[int(textid) for textid in cutVotes.opposition_abstain_max_org.split(',')])],
                    'score': cutVotes.opposition_abstain_max
                },
                "avgOpposition": {'score': cutVotes.opposition_abstain},
                "avgCoalition": {'score': cutVotes.coalition_abstain},
            },
            "against": {
                'score': cutVotes.this_against,
                'maxCoalition': {
                    'mps': [{'name': org.name, 'id': org.id_parladata} for org in Organization.objects.filter(id_parladata__in=[int(textid) for textid in cutVotes.coalition_against_max_org.split(',')])],
                    'score': cutVotes.coalition_against_max
                },
                'maxOpposition': {
                    'mps': [{'name': org.name, 'id': org.id_parladata} for org in Organization.objects.filter(id_parladata__in=[int(textid) for textid in cutVotes.opposition_against_max_org.split(',')])],
                    'score': cutVotes.opposition_against_max
                },
                "avgOpposition": {'score': cutVotes.opposition_against},
                "avgCoalition": {'score': cutVotes.coalition_against},
            },
            "absent": {
                'score': cutVotes.this_absent,
                'maxCoalition': {
                    'mps': [{'name': org.name, 'id': org.id_parladata} for org in Organization.objects.filter(id_parladata__in=[int(textid) for textid in cutVotes.coalition_absent_max_org.split(',')])],
                    'score': cutVotes.coalition_absent_max
                },
                'maxOpposition': {
                    'mps': [{'name': org.name, 'id': org.id_parladata} for org in Organization.objects.filter(id_parladata__in=[int(textid) for textid in cutVotes.opposition_absent_max_org.split(',')])],
                    'score': cutVotes.opposition_absent_max
                },
                "avgOpposition": {'score': cutVotes.opposition_absent},
                "avgCoalition": {'score': cutVotes.coalition_absent},
            },
            'for': {
                'score': cutVotes.this_for,
                'maxCoalition': {
                    'mps': [{'name': org.name, 'id': org.id_parladata} for org in Organization.objects.filter(id_parladata__in=[int(textid) for textid in cutVotes.coalition_for_max_org.split(',')])],
                    'score': cutVotes.coalition_for_max
                },
                'maxOpposition': {
                    'mps': [{'name': org.name, 'id': org.id_parladata} for org in Organization.objects.filter(id_parladata__in=[int(textid) for textid in cutVotes.opposition_for_max_org.split(',')])],
                    'score': cutVotes.opposition_for_max
                },
                "avgOpposition": {'score': cutVotes.opposition_for},
                "avgCoalition": {'score': cutVotes.coalition_for},
            },
        }
    }
    return JsonResponse(out)


# get PGs IDs
def getPGsIDs(request):
    output = []
    data = requests.get(API_URL+'/getAllPGs/')
    data = data.json()

    output = {"members": [i for i in data], "lastDate": Session.objects.all().order_by("-start_time")[0].start_time.strftime(API_DATE_FORMAT)}

    return JsonResponse(output, safe=False)


def runSetters(request, date_to):
    setters_models = {
        # not working yet #LastActivity: BASE_URL+'/p/setLastActivity/',
        CutVotes: setCutVotes,#BASE_URL+'/p/setCutVotes/',
        DeviationInOrganization: setDeviationInOrg,
        LessMatchingThem: setLessMatchingThem,
        MostMatchingThem: setMostMatchingThem
    }

    IDs = getPGIDs()
    IDs = [1, 2]
    # print IDs
    allIds = len(IDs)
    curentId = 0
    
    for model, setter in setters_models.items():
        for ID in IDs:
            print setter
            dates = findDatesFromLastCard(model, ID, date_to)
            print dates
            for date in dates:
                print date.strftime(API_DATE_FORMAT)
                # print setter + str(ID) + "/" + date.strftime(API_DATE_FORMAT)
                setter(request, str(ID), date.strftime(API_DATE_FORMAT))
        curentId += 1
                # result = requests.get(setter + str(ID) + "/" + date.strftime(API_DATE_FORMAT)).status_code
    return JsonResponse({"status": "all is fine :D"}, safe=False)


def runSetters(date_to):
    setters_models = {
        # not working yet #LastActivity: BASE_URL+'/p/setLastActivity/',
        CutVotes: "/setCutVotes/",#BASE_URL+'/p/setCutVotes/',
        DeviationInOrganization: "/setDeviationInOrg/",
        LessMatchingThem: "/setLessMatchingThem/",
        MostMatchingThem: "/setMostMatchingThem/"
    }

    IDs = getPGIDs()
    IDs = [1, 2]
    # print IDs
    allIds = len(IDs)
    curentId = 0
    
    for model, setter in setters_models.items():
        for ID in IDs:
            print setter
            dates = findDatesFromLastCard(model, ID, date_to)
            print dates
            for date in dates:
                url = BASE_URL+"/pg"+setter+str(ID)+'/'+date.strftime(API_DATE_FORMAT)
                print url
                # print setter + str(ID) + "/" + date.strftime(API_DATE_FORMAT)
                a = requests.get(url)
        curentId += 1
                # result = requests.get(setter + str(ID) + "/" + date.strftime(API_DATE_FORMAT)).status_code
    return {"status": "all is fine :D"}