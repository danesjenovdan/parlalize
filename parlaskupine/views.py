# -*- coding: UTF-8 -*-
from parlalize.utils import *
import requests
import json
from django.http import JsonResponse
from parlaskupine.models import *
from parlaseje.models import Activity,Session
from collections import Counter
from parlalize.settings import API_URL, API_DATE_FORMAT, BASE_URL
import numpy as np
from scipy.stats.stats import pearsonr
from parlaposlanci.models import Person
from parlaposlanci.views import getMPsList
import math

# Create your views here.


def setBasicInfOfPG(request, pg_id, date_):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()
    data = requests.get(API_URL+'/getBasicInfOfPG/'+str(pg_id)+'/').json()
#vprasi za shranjevanje yes and no
    result = saveOrAbort(model=PGStatic,
                         created_for=date_of,
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

def setPercentOFAttendedSessionPG(request, pg_id, date_=None):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = findDatesFromLastCard(PercentOFAttendedSession, pg_id, datetime.now().date())[0]

    allSum = {}
    data = {}

    membersOfPG = requests.get(API_URL+'/getMembersOfPGsOnDate/'+date_).json()
    data = requests.get(API_URL+'/getNumberOfAllMPAttendedSessions/'+date_).json()

    sessions = {pg:[] for pg in membersOfPG if membersOfPG[pg]}
    votes = {pg:[] for pg in membersOfPG if membersOfPG[pg]}
    for pg in membersOfPG:
        if not membersOfPG[pg]:
            continue
        for member in membersOfPG[pg]:
            sessions[pg].append(data["sessions"][str(member)])
            votes[pg].append(data["votes"][str(member)])
        sessions[pg] = sum(sessions[pg])/len(sessions[pg])
        votes[pg] = sum(votes[pg])/len(votes[pg])

    thisMPSessions = sessions[pg_id]
    maximumSessions = max(sessions.values())
    maximumPGSessions = [pgId for pgId in sessions if sessions[pgId]==maximumSessions]
    averageSessions = sum(data["sessions"].values()) / len(data["sessions"])

    thisMPVotes = votes[pg_id]
    maximumVotes = max(votes.values())
    maximumPGVotes = [pgId for pgId in votes if votes[pgId]==maximumVotes]
    averageVotes = sum(data["votes"].values()) / len(data["votes"])

    #kaksen bo interfejs ko bo imela prav ta PG maksimum
    result = saveOrAbortNew(model=PercentOFAttendedSession,
                         created_for=date_of,
                         organization=Organization.objects.get(id_parladata=int(pg_id)),
                         organization_value_sessions = thisMPSessions,
                         maxPG_sessions=maximumPGSessions,
                         average_sessions=averageSessions,
                         maximum_sessions=maximumSessions,
                         organization_value_votes = thisMPVotes,
                         maxPG_votes=maximumPGVotes,
                         average_votes=averageVotes,
                         maximum_votes=maximumVotes)

    return JsonResponse({'alliswell': True})

def getPercentOFAttendedSessionPG(request, pg_id, date_=None):

    card = getPGCardModelNew(PercentOFAttendedSession, pg_id, date_)

    # uprasi ce isto kot pri personu razdelimo
    data = {
           'organization': {
                'name': card.organization.name,
                'id': card.organization.id
                },
           "sessions":{
                'organization_value':card.organization_value_sessions,
                'maxPG':card.maxPG_sessions,
                'average':card.average_sessions,
                'maximum':card.maximum_sessions,
                },
            "votes":{
                'organization_value':card.organization_value_votes,
                'maxPG':card.maxPG_votes,
                'average':card.average_votes,
                'maximum':card.maximum_votes,
                }
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


def getSpeechesOfPG(request, pg_id, date_=False):
  if date_:
    allSessions = Session.objects.filter(start_time__lte=datetime.strptime(date_, '%d.%m.%Y').date())
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


def howMatchingThem(request, pg_id, type_of, date_=None):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()

    pg_score, membersInPGs, votes, all_votes = getRangeVotes([pg_id], date_, "logic")

    # most match them
    if type_of == "match":
        for voter in membersInPGs[str(pg_id)]:
            votes.pop(str(voter))

    # deviation in PG
    if type_of == "deviation":
        del membersInPGs[str(pg_id)]
        for pgs in membersInPGs.keys():
            for voter in membersInPGs[str(pgs)]:
                votes.pop(str(voter))


    members = getMPsList(request, date_)
    membersDict = {str(mp['id']): mp for mp in json.loads(members.content)}

    #calculate parsonr
    out = {person: (pearsonr(list(pg_score), [votes[str(person)][str(val)] for val in all_votes])[0]+1)*50 for person in sorted(votes.keys())}

    for person in out.keys():
        if math.isnan(out[person]):
            out.pop(person, None)

    keys = sorted(out, key=out.get)
    key4remove = []
    for key in keys:
        # if members isn't member in this time skip him
        if key not in membersDict.keys():
            key4remove.append(key)
            continue
        membersDict[str(key)].update({'ratio': out[str(key)]})
        membersDict[key].update({'id': key})

    #remove keys of members which isn't member in this time
    for key in key4remove:
        keys.remove(key)
    return membersDict, keys, date_of


def setMostMatchingThem(request, pg_id, date_=None):
    if date_:
        members, keys, date_of = howMatchingThem(request, pg_id, date_=date_, type_of="match")
    else:
        members, keys, date_of = howMatchingThem(request, pg_id, type_of="match")

    out = {index: members[key] for key, index in zip(keys[-6:-1], [5, 4, 3, 2, 1])}
    #print out
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


def setLessMatchingThem(request, pg_id, date_=None):
    if date_:
        members, keys, date_of = howMatchingThem(request, pg_id, date_=date_, type_of="match")
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


def setDeviationInOrg(request, pg_id, date_=None):
    if date_:
        members, keys, date_of = howMatchingThem(request, pg_id, date_=date_, type_of="deviation")
    else:
        members, keys, date_of = howMatchingThem(request, pg_id, type_of="deviation")

    numOfKeys = len(keys)

    out = {index: members[key] for key, index in zip(keys[:3], [1, 2, 3])}
    out.update({index: members[key] for key, index in zip(keys[-3:], [4, 5, 6])})
    try:
        result = saveOrAbortNew(model=DeviationInOrganization,
                                created_for=date_of,
                                organization=Organization.objects.get(id_parladata=int(pg_id)),
                                person1=Person.objects.get(id_parladata=int(out[1]['id'])) if numOfKeys > 0 else None,
                                votes1=out[1]['ratio'] if numOfKeys > 0 else None,
                                person2=Person.objects.get(id_parladata=int(out[2]['id'])) if numOfKeys > 1 else None,
                                votes2=out[2]['ratio'] if numOfKeys > 1 else None,
                                person3=Person.objects.get(id_parladata=int(out[3]['id'])) if numOfKeys > 2 else None,
                                votes3=out[3]['ratio'] if numOfKeys > 2 else None,
                                person4=Person.objects.get(id_parladata=int(out[4]['id'])) if numOfKeys > 3 else None,
                                votes4=out[4]['ratio'] if numOfKeys > 3 else None,
                                person5=Person.objects.get(id_parladata=int(out[5]['id'])) if numOfKeys > 4 else None,
                                votes5=out[5]['ratio'] if numOfKeys > 4 else None,
                                person6=Person.objects.get(id_parladata=int(out[6]['id'])) if numOfKeys > 5 else None,
                                votes6=out[6]['ratio'] if numOfKeys > 5 else None,
                                )

        return JsonResponse({'alliswell': True})
    except:
        return JsonResponse({'alliswell': False})


def getMPStaticPersonData(id_, date_):
    try:
        return requests.get(BASE_URL+'/p/getMPStatic/'+str(id_)+"/"+date_).json()["person"]
    except:
        return {}


def getMostMatchingThem(request, pg_id, date_=None):
    mostMatching = getPGCardModelNew(MostMatchingThem, pg_id, date_)
    if not date_:
        date_=""
    out = {
        'organization': {
            'name': Organization.objects.get(id_parladata=int(pg_id)).name,
            'id': int(pg_id)
        },
        'results': [
            {
                "ratio": mostMatching.votes1,
                "person": getMPStaticPersonData(mostMatching.person1.id_parladata, date_)
            },
            {
                "ratio": mostMatching.votes2,
                "person": getMPStaticPersonData(mostMatching.person2.id_parladata, date_)
            },
            {
                "ratio": mostMatching.votes3,
                "person": getMPStaticPersonData(mostMatching.person3.id_parladata, date_)
            },
            {
                "ratio": mostMatching.votes4,
                "person": getMPStaticPersonData(mostMatching.person4.id_parladata, date_)
            },
            {
                "ratio": mostMatching.votes5,
                "person": getMPStaticPersonData(mostMatching.person5.id_parladata, date_)
            }
        ]
    }

    return JsonResponse(out, safe=False)


def getLessMatchingThem(request, pg_id, date_=None):
    mostMatching = getPGCardModelNew(LessMatchingThem, pg_id, date_)
    if not date_:
        date_=""
    out = {
        'organization': {
            'name': Organization.objects.get(id_parladata=int(pg_id)).name,
            'id': int(pg_id)
        },
        'results': [
            {
                "ratio": mostMatching.votes1,
                "person": getMPStaticPersonData(mostMatching.person1.id_parladata, date_)
            },
            {
                "ratio": mostMatching.votes2,
                "person": getMPStaticPersonData(mostMatching.person2.id_parladata, date_)
            },
            {
                "ratio": mostMatching.votes3,
                "person": getMPStaticPersonData(mostMatching.person3.id_parladata, date_)
            },
            {
                "ratio": mostMatching.votes4,
                "person": getMPStaticPersonData(mostMatching.person4.id_parladata, date_)
            },
            {
                "ratio": mostMatching.votes5,
                "person": getMPStaticPersonData(mostMatching.person5.id_parladata, date_)
            }
        ]
    }
    return JsonResponse(out, safe=False)


def getDeviationInOrg(request, pg_id, date_=None):
    mostMatching = getPGCardModelNew(DeviationInOrganization, pg_id, date_)
    if not date_:
        date_=""
    out = {
        'organization': {
            'name': Organization.objects.get(id_parladata=int(pg_id)).name,
            'id': int(pg_id)
        },
        'results': [
            {
                "ratio": mostMatching.votes1,
                "person": getMPStaticPersonData(mostMatching.person1.id_parladata, date_)
            },
            {
                "ratio": mostMatching.votes2,
                "person": getMPStaticPersonData(mostMatching.person2.id_parladata, date_)
            } if mostMatching.votes2 else None,
            {
                "ratio": mostMatching.votes3,
                "person": getMPStaticPersonData(mostMatching.person3.id_parladata, date_)
            } if mostMatching.votes3 else None,
            {
                "ratio": mostMatching.votes4,
                "person": getMPStaticPersonData(mostMatching.person4.id_parladata, date_)
            } if mostMatching.votes4 else None,
            {
                "ratio": mostMatching.votes5,
                "person": getMPStaticPersonData(mostMatching.person5.id_parladata, date_)
            } if mostMatching.votes5 else None,
            {
                "ratio": mostMatching.votes6,
                "person": getMPStaticPersonData(mostMatching.person6.id_parladata, date_)
            } if mostMatching.votes6 else None,
        ]
    }
    #remove None from list. If PG dont have 6 members.
    out["results"] = filter(lambda a: a != None, out["results"])
    return JsonResponse(out, safe=False)


def setCutVotes(request, pg_id, date_=None):
    def getMaxOrgData(data, ids):
        d = {str(pg): data[pg] for pg in ids}
        return ",".join([key for key,val in d.iteritems() if val == max(d.values())])

    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()

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

    pg_score_C, membersInPGs, votes, all_votes = getRangeVotes(coal_pgs, date_, "plain")
    pg_score_O, membersInPGs, votes, all_votes = getRangeVotes(oppo_pgs, date_, "plain")


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
    coal_avg["for"] = int((float(sum(map(voteFor, pg_score_C)))/float(len(pg_score_C)))*100)
    oppo_avg["for"] = int((float(sum(map(voteFor, pg_score_O)))/float(len(pg_score_O)))*100)
    coal_avg["against"] = int((float(sum(map(voteAgainst, pg_score_C)))/float(len(pg_score_C)))*100)
    oppo_avg["against"] = int((float(sum(map(voteAgainst, pg_score_O)))/float(len(pg_score_O)))*100)
    coal_avg["abstain"] = int((float(sum(map(voteAbstain, pg_score_C)))/float(len(pg_score_C)))*100)
    oppo_avg["abstain"] = int((float(sum(map(voteAbstain, pg_score_O)))/float(len(pg_score_O)))*100)
    coal_avg["absent"] = int((float(sum(map(voteAbsent, pg_score_C)))/float(len(pg_score_C)))*100)
    oppo_avg["absent"] = int((float(sum(map(voteAbsent, pg_score_O)))/float(len(pg_score_O)))*100)

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

    output = {"list": [i for i in data], "lastDate": Session.objects.all().order_by("-start_time")[0].start_time.strftime(API_DATE_FORMAT)}

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
    #IDs = [1, 2]
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
