# -*- coding: UTF-8 -*-
from django.http import JsonResponse
from scipy.stats.stats import pearsonr
from datetime import date, datetime, timedelta

import numpy
from parlalize.utils import *
import requests
import json
from datetime import datetime
from django.http import HttpResponse
import string
from kvalifikatorji.scripts import numberOfWords, countWords, getScore, getScores, problematicno, privzdignjeno, preprosto, TFIDF, getCountList
from collections import Counter
from parlalize.settings import LAST_ACTIVITY_COUNT
from .models import *
from parlalize.settings import API_URL, API_DATE_FORMAT, API_OUT_DATE_FORMAT
from parlaseje.models import Session, Tag
from utils.speech import WordAnalysis

from kompas2 import notes

# Create your views here.

#get List of MPs
def getMPsList(request, date_=None):
    output = []
    if date_:
        data = requests.get(API_URL+'/getMPs/'+date_)
    else:
        data = requests.get(API_URL+'/getMPs/')
    data = data.json()

    output = [{'id': i['id'], 'image': i['image'], 'name': i['name'], 'membership': i['membership'], 'acronym': i['acronym'], 'district': i['district']} for i in data]

    return JsonResponse(output, safe=False)


##returns MP static data like PoliticalParty, age, ....
def setMPStaticPL(request, person_id, date_=None):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
        data = requests.get(API_URL+'/getMPStatic/' + person_id + "/" + date_).json()
    else:
        date_of = datetime.now().date()
        data = requests.get(API_URL+'/getMPStatic/'+ person_id).json()

    if not data:
        return JsonResponse({"status":'Nothing iz well', "saved": False})
    dic = dict()

    result = saveOrAbortNew(model=MPStaticPL,
                            created_for=date_of,
                            person=Person.objects.get(id_parladata=int(person_id)),
                            voters=data['voters'], age=data['age'],
                            mandates=data['mandates'],
                            party_id=data['party_id'],
                            education=data['education'],
                            previous_occupation=data['previous_occupation'],
                            name=data['name'],
                            district=data['district'],
                            facebook=data['social']['facebook'],
                            twitter=data['social']['twitter'],
                            linkedin=data['social']['linkedin'],
                            party_name=data['party'],
                            acronym=data['acronym'],
                            gov_id=data['gov_id'],
                            gender=data['gender'])

    if result:
        for group in data['groups']:
            new_group = MPStaticGroup(person=MPStaticPL.objects.filter(person__id_parladata=int(person_id)).latest('created_at'), groupid=int(group['id']), groupname=group['name'])
            new_group.save()

    return JsonResponse({"status":'All iz well', "saved":result})


def getMPStaticPL(request, person_id, date_=None):
    card = getPersonCardModelNew(MPStaticPL, person_id, date_)

    if card.twitter == 'False': print card.twitter

    data = {
        'date_of_card':card.created_for.strftime(API_DATE_FORMAT),
        'person': getPersonData(person_id, date_),
        'results': {
            'voters': card.voters,
            'age': card.age,
            'mandates': card.mandates,
            'party_id': card.party_id,
            'acronym': card.acronym,
            'education': card.education,
            'previous_occupation': card.previous_occupation,
            'name': card.name,
            'district': card.district,
            'party': card.party_name,
            'social': [{'facebook': card.facebook if card.facebook != 'False' else None, 'twitter': card.twitter if card.twitter != 'False' else None, 'linkedin': card.linkedin if card.linkedin != 'False' else None}],
            'groups': [{'group_id': group.groupid, 'group_name': group.groupname} for group in card.mpstaticgroup_set.all()]
        }
    }

    return JsonResponse(data)


#Saves to DB percent of attended sessions of MP and maximum and average of attended sessions
def setPercentOFAttendedSession(request, person_id, date_=None):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = findDatesFromLastCard(Presence, person_id, datetime.now().date())[0]
    data = requests.get(API_URL+'/getNumberOfAllMPAttendedSessions/'+date_).json()
    thisMP = data["sessions"][person_id]
    maximum = max(data["sessions"].values())
    maximumMP = [pId for pId in data["sessions"] if data["sessions"][pId]==maximum]
    average = sum(data["sessions"].values()) / len(data["sessions"])

    thisMPVotes = data["votes"][person_id]
    maximumVotes = max(data["votes"].values())
    maximumMPVotes = [pId for pId in data["votes"] if data["votes"][pId]==maximumVotes]
    averageVotes = sum(data["votes"].values()) / len(data["votes"])

    result = saveOrAbortNew(model=Presence,
                         created_for=date_of,
                         person=Person.objects.get(id_parladata=int(person_id)),
                         person_value_sessions=thisMP,
                         maxMP_sessions=maximumMP,
                         average_sessions=average,
                         maximum_sessions=maximum,
                         person_value_votes=thisMPVotes,
                         maxMP_votes=maximumMPVotes,
                         average_votes=averageVotes,
                         maximum_votes=maximumVotes)

    return JsonResponse({'alliswell': result})

def getPercentOFAttendedSession(request, person_id, date=None):
    equalVoters = getPersonCardModelNew(Presence, person_id, date)

    out  = {
        'person': getPersonData(person_id, date),
        'results': {
            "sessions":{
                "score": equalVoters.person_value_sessions,
                "average": equalVoters.average_sessions,
                "max": {
                    "mps": [getPersonData(person, date) for person in equalVoters.maxMP_sessions],
                    "score": equalVoters.maximum_sessions,
                }
            },
            "votes": {
                "score": equalVoters.person_value_votes,
                "average": equalVoters.average_votes,
                "max": {
                    "mps": [getPersonData(person, date) for person in equalVoters.maxMP_votes],
                    "score": equalVoters.maximum_votes,
                }
            }
        }
    }
    return JsonResponse(out)


#Depricated
#Saves to DB number of spoken word of MP and maximum and average of spoken words
def setNumberOfSpokenWordsALL(request, date_=None):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()
        date_=""
    print '[INFO] Getting MPs'
    mps = requests.get(API_URL+'/getMPs/'+date_).json()

    mp_results = []

    for mp in mps:
        print '[INFO] Pasting speeches for MP ' + str(mp['id'])
        speeches = requests.get(API_URL+'/getSpeeches/' + str(mp['id']) + "/" + date_).json()

        text = ''.join([speech['content'] for speech in speeches])

        mp_results.append({'person_id': mp['id'], 'wordcount': numberOfWords(text)})

    print '[INFO] Sorting MPs'
    mps_sorted = sorted(mp_results, key=lambda k: k['wordcount'])

    print '[INFO] Getting all speeches'
    all_speeches = requests.get(API_URL+'/getAllSpeeches/'+date_).json()
    print '[INFO] Joining all speeches'
    text = ''.join([speech['content'] for speech in all_speeches])

    print '[INFO] Calculating total words'
    total_words = numberOfWords(text)
    print '[INFO] Calculating average words'
    average_words = total_words/len(mps)

    for result in mp_results:
        print '[INFO] Saving or updating MP\'s results'
        print saveOrAbortNew(model=SpokenWords,
                             created_for=date_of,
                             person=Person.objects.get(id_parladata=int(result['person_id'])),
                             score=int(result['wordcount']),
                             maxMP=Person.objects.get(id_parladata=int(mps_sorted[-1]['person_id'])),
                             average=average_words,
                             maximum=mps_sorted[-1]['wordcount'])

    return HttpResponse('All iz well')

def getNumberOfSpokenWords(request, person_id, date=None):

    card = getPersonCardModelNew(SpokenWords, person_id, date)

    results = {
        'person': getPersonData(person_id, date),
        'results': {
            'score': card.score,
            'average': card.average,
            'max': {
                'mps': [
                    getPersonData(card.maxMP.id_parladata, date)
                ],
                'score': card.maximum
            }
        }
    }
    return JsonResponse(results)

def setLastActivity(request, person_id):
    out = []
    activites = {date:[activity.get_child() for activity in Activity.objects.filter(person__id_parladata=person_id, start_time__range=[date, date+timedelta(days=1)])] for date in Activity.objects.filter(person__id_parladata=person_id).order_by("start_time").datetimes('start_time', 'day')}
    result = []
    for date in activites.keys():
        avtivity_ids = []
        options = []
        result = []
        vote_name = []
        types = []
        sessions = []
        for acti in  activites[date]:
            #print acti.id_parladata
            if type(acti) == Speech:
                #print "Speech"
                avtivity_ids.append(acti.id_parladata)
                types.append("speech")
                vote_name.append(acti.session.name)
                result.append("None")
                options.append("None")
                sessions.append(str(acti.session.id))
            else:
                #print "Ballot"
                avtivity_ids.append(acti.vote.id_parladata)
                types.append("ballot")
                vote_name.append(acti.vote.motion)
                result.append(acti.vote.result)
                options.append(acti.option)
                sessions.append("None")

        out.append(saveOrAbortNew(model=LastActivity,
                                  person=Person.objects.get(id_parladata=int(person_id)),
                                  created_for=date,
                                  activity_id=";".join(map(str, avtivity_ids)),
                                  option=";".join(map(str, options)),
                                  result=";".join(map(str, result)),
                                  vote_name=";".join(vote_name),
                                  typee=";".join(types),
                                  session_id=";".join(sessions)))

    return JsonResponse(out, safe=False)

def getLastActivity(request, person_id, date_=None):
    print date

    def parseDayActivites(day_activites):
        data = []
        types = day_activites.typee.split(";")
        vote_names = day_activites.vote_name.split(";")
        results = day_activites.result.split(";")
        options = day_activites.option.split(";")
        activity_ids = day_activites.activity_id.split(";")
        sessions_ids = day_activites.session_id.split(";")
        for i in range(len(day_activites.typee.split(";"))):
            if types[i] == "ballot":
                data.append({
                    "option": options[i],
                    "result": Vote.objects.filter(id_parladata=activity_ids[i]).order_by("-created_at")[0].result,
                    "vote_name": vote_names[i],
                    "vote_id": int(activity_ids[i]),
                    "type": types[i],
                    "session_id": Vote.objects.filter(id_parladata=int(activity_ids[i])).order_by("-created_at")[0].session.id
                    })
            elif types[i] == "speech":
                data.append({
                    "speech_id": int(activity_ids[i]),
                    "type": types[i],
                    "session_name": vote_names[i],
                    "session_id": sessions_ids[i]
                    })
        return {"date": day_activites.created_for.strftime(API_OUT_DATE_FORMAT), "events": data}

    out = []

    lastActivites = getPersonCardModelNew(LastActivity, person_id, date_)
    lastDay = lastActivites.created_for.strftime(API_OUT_DATE_FORMAT)
    out.append(parseDayActivites(lastActivites))
    for i in range(LAST_ACTIVITY_COUNT - 1):
        startDate = lastActivites.created_for - timedelta(days=1)
        lastActivites = getPersonCardModelNew(LastActivity, person_id, datetime.strftime(startDate, "%d.%m.%Y"))
        if lastActivites == None:
            break;
        out.append(parseDayActivites(lastActivites))

    static = getPersonCardModelNew(MPStaticPL, person_id, date_)

    result = {
        'date_of_card':lastDay,
        'person': getPersonData(person_id, date_),
        'results': out
        }
    return JsonResponse(result, safe=False)

#TODO date
def getAllSpeeches(request, person_id, date_=None):
    speeches = Speech.objects.filter(person__id_parladata=person_id)
    if date_:
        print date_
        speeches = [[speech for speech in speeches.filter(start_time__range=[t_date, t_date+timedelta(days=1)])] for t_date in speeches.filter(start_time__lte=datetime.strptime(date_, '%d.%m.%Y')).order_by("start_time").datetimes('start_time', 'day')]
    else:
        speeches = [[speech for speech in speeches.filter(start_time__range=[t_date, t_date+timedelta(days=1)])] for t_date in speeches.order_by("start_time").datetimes('start_time', 'day')]
    out = []
    for day in speeches:
        dayData = {"date": day[0].start_time.strftime(API_OUT_DATE_FORMAT), "speeches":[]}
        for speech in day:
            dayData["speeches"].append({
                "session_name": speech.session.name,
                "speech_id": speech.id_parladata,
                "session_id": speech.session.id_parladata})
        out.append(dayData)



    result  = {
        'person': getPersonData(person_id, date_),
        'results': list(reversed(out))
        }
    return JsonResponse(result, safe=False)


#method returns percent, how similar does the members vote
def getEqualVoters(request, id, date_=None):
    print id
    if date_:
        votes = getLogicVotes(date_)
        date_of = datetime.strptime(date_, '%d.%m.%Y')
    else:
        votes = getLogicVotes()
        date_of = datetime.now().date()

    members = getMPsList(request, date_)
    membersDict = {str(mp['id']):mp for mp in json.loads(members.content)}
    tempVotes = {voter: votes_ for voter, votes_ in votes.items() if voter in membersDict.keys()}
    votes = tempVotes
    out = {vote:pearsonr(votes[str(id)].values(), votes[str(vote)].values())[0] for vote in sorted(votes.keys())}
    keys = sorted(out, key=out.get)

    for key in keys:
        membersDict[key].update({'ratio':out[str(key)]})
        membersDict[key].update({'id':key})
    return membersDict, keys, date_of


# Method return json with most similar voters to this voter
def setMostEqualVoters(request, person_id, date_=None):
    if date_:
        members, keys, date_of = getEqualVoters(request, person_id, date_)
    else:
        members, keys, date_of = getEqualVoters(request, person_id)

    out = {index: members[key] for key, index in zip(keys[-6:-1], [5, 4, 3, 2, 1])}

    result = saveOrAbortNew(model=EqualVoters,
                            created_for=date_of,
                            person=Person.objects.get(id_parladata=int(person_id)),
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
    return HttpResponse('All iz well')


def getMostEqualVoters(request, person_id, date_=None):
    equalVoters = getPersonCardModelNew(EqualVoters, person_id, date_)

    print equalVoters.person1.id_parladata

    out = {
        'date_of_card':equalVoters.created_for.strftime(API_OUT_DATE_FORMAT),
        'person': getPersonData(person_id, date_),
        'results': [
            {
                "ratio": equalVoters.votes1,
                "person": getPersonData(equalVoters.person1.id_parladata, date_),
            },
            {
                "ratio": equalVoters.votes2,
                "person": getPersonData(equalVoters.person2.id_parladata, date_),
            },
            {
                "ratio": equalVoters.votes3,
                "person": getPersonData(equalVoters.person3.id_parladata, date_),
            },
            {
                "ratio": equalVoters.votes4,
                "person": getPersonData(equalVoters.person4.id_parladata, date_),
            },
            {
                "ratio": equalVoters.votes5,
                "person": getPersonData(equalVoters.person5.id_parladata, date_),
            }
        ]
    }

    #data = getPersonCardModel(EqualVoters, person_id)
    return JsonResponse(out, safe=False)


# Method return json with less similar voters to this voter
def setLessEqualVoters(request, person_id, date_=None):
    if date_:
        members, keys, date_of = getEqualVoters(request, person_id, date_)
    else:
        members, keys, date_of = getEqualVoters(request, person_id)
    out = {index: members[key] for key, index in zip(keys[:5], [1, 2, 3, 4, 5])}

    result = saveOrAbortNew(model=LessEqualVoters,
                            created_for=date_of,
                            person=Person.objects.get(id_parladata=int(person_id)),
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
    return HttpResponse('All iz well')


def getLessEqualVoters(request, person_id, date_=None):
    equalVoters = getPersonCardModelNew(LessEqualVoters, person_id, date_)
    out = {
        'date_of_card':equalVoters.created_for.strftime(API_OUT_DATE_FORMAT),
        'person': getPersonData(person_id, date_),
        'results': [
            {
                "ratio": equalVoters.votes1,
                "person": getPersonData(equalVoters.person1.id_parladata, date_),
            },
            {
                "ratio": equalVoters.votes2,
                "person": getPersonData(equalVoters.person2.id_parladata, date_),
            },
            {
                "ratio": equalVoters.votes3,
                "person": getPersonData(equalVoters.person3.id_parladata, date_),
            },
            {
                "ratio": equalVoters.votes4,
                "person": getPersonData(equalVoters.person4.id_parladata, date_),
            },
            {
                "ratio": equalVoters.votes5,
                "person": getPersonData(equalVoters.person5.id_parladata, date_),
            }
        ]
    }

    #data = getPersonCardModel(EqualVoters, person_id)
    return JsonResponse(out, safe=False)

#get speech and data of speaker
def getSpeech(request, id):
    speech=requests.get(API_URL+'/getSpeech/'+id+'/')
    speech = speech.json()
    memList = getMPsList(request)
    members = json.loads(memList.content)
    speech['name'] = members[str(speech['speeker'])]['Name']
    speech['image'] = members[str(speech['speeker'])]['Image']
    return JsonResponse(speech)

#TODO
#/id/percent/prisotniAliVsi
#/34/66/1
def getMPsWhichFitsToPG(request, id):
    r=requests.get(API_URL+'/getVotes/')
    votes = r.json()
    r=requests.get(API_URL+'/getMembersOfPGs/')
    membersInPGs = r.json()

    votesToLogical(votes, len(Vote.objects.all()))
    #calculate mean
    votesLists = [votes[str(pgMember)] for pgMember in membersInPGs[id]]
    votesArray = numpy.array(votesLists)
    mean = numpy.mean(votesArray, axis=0)

    #TODO discretization for
    #mean = [for m in mean]

    #delete members of PR from votes list
    map(votes.__delitem__, [str(member) for member in membersInPGs[id]])

    out = {vote:pearsonr(votes[vote], mean)[0] for vote in votes.keys()}
    keys = sorted(out, key=out.get)
    print out
    members = getMPsList(request)
    members= json.loads(members.content)
    print members
    for member in members:
        #TODO: check members group
        try:
            member.update({'ratio': out[str(member["id"])]})
        except:
            member.update({'ratio': 0})
    #for key in keys:
    #   members[key].update({'ratio':out[key]})
    outs = sorted(members, key=lambda k: k['ratio'])

    #outs = {key:members[key] for key in keys[-5:]}
    return JsonResponse(outs[-5:], safe=False)


def setCutVotes(request, person_id, date_=None):
    print "cut"
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT)
    else:
        date_of = datetime.now().date()

    r=requests.get(API_URL+'/getCoalitionPGs/')
    coalition = r.json()

    coal_pgs = [str(pg) for pg in coalition["coalition"]]
    oppo_pgs = [str(pg) for pg in coalition["opposition"]]

    pg_score_C, membersInPGs, votes, all_votes = getRangeVotes(coal_pgs, date_, "plain")
    pg_score_O, membersInPGs, votes, all_votes = getRangeVotes(oppo_pgs, date_, "plain")

    coal_avg = {}
    oppo_avg = {}


    # Calculate coalition and opposition average
    coal_avg["for"] = (float(sum(map(voteFor, pg_score_C)))/float(len(pg_score_C)))*100
    oppo_avg["for"] = (float(sum(map(voteFor, pg_score_O)))/float(len(pg_score_O)))*100
    coal_avg["against"] = (float(sum(map(voteAgainst, pg_score_C)))/float(len(pg_score_C)))*100
    oppo_avg["against"] = (float(sum(map(voteAgainst, pg_score_O)))/float(len(pg_score_O)))*100
    coal_avg["abstain"] = (float(sum(map(voteAbstain, pg_score_C)))/float(len(pg_score_C)))*100
    oppo_avg["abstain"] = (float(sum(map(voteAbstain, pg_score_O)))/float(len(pg_score_O)))*100
    coal_avg["absent"] = (float(sum(map(voteAbsent, pg_score_C)))/float(len(pg_score_C)))*100
    oppo_avg["absent"] = (float(sum(map(voteAbsent, pg_score_O)))/float(len(pg_score_O)))*100

    memList = getMPsList(request, date_)
    members = {str(mp['id']):mp for mp in json.loads(memList.content)}

    out = dict()
    out["for"] = dict()
    out["against"] = dict()
    out["abstain"] = dict()
    out["absent"] = dict()
    #Calculations for this member
    out["for"]["this"]=float(sum(map(voteFor, votes[person_id].values())))/float(len(votes[person_id].values()))*100
    out["against"]["this"]=float(sum(map(voteAgainst, votes[person_id].values())))/float(len(votes[person_id].values()))*100
    out["abstain"]["this"]=float(sum(map(voteAbstain, votes[person_id].values())))/float(len(votes[person_id].values()))*100
    out["absent"]["this"]=float(sum(map(voteAbsent, votes[person_id].values())))/float(len(votes[person_id].values()))*100
    memReq = getMPStaticPL(request, person_id)
    memberData = json.loads(memReq.content)
    out["thisName"]=memberData['person']['name']

    #Calculations for coalition
    idsForCoal, coalFor = zip(*[(member,float(sum(map(voteFor,votes[str(member)].values())))/float(len(votes[str(member)].values()))*100) for i in coalition['coalition'] for member in membersInPGs[str(i)] if len(votes[str(member)].values()) > 0])
    idsCoalAgainst, coalAgainst = zip(*[(member,float(sum(map(voteAgainst,votes[str(member)].values())))/float(len(votes[str(member)].values()))*100) for i in coalition['coalition'] for member in membersInPGs[str(i)] if len(votes[str(member)].values()) > 0])
    idsCoalAbstain, coalAbstain = zip(*[(member,float(sum(map(voteAbstain,votes[str(member)].values())))/float(len(votes[str(member)].values()))*100) for i in coalition['coalition'] for member in membersInPGs[str(i)] if len(votes[str(member)].values()) > 0])
    idsCoalAbsent, coalAbsent = zip(*[(member,float(sum(map(voteAbsent,votes[str(member)].values())))/float(len(votes[str(member)].values()))*100) for i in coalition['coalition'] for member in membersInPGs[str(i)] if len(votes[str(member)].values()) > 0])

    coalMaxPercentFor = max(coalFor)
    coalMaxPercentAgainst = max(coalAgainst)
    coalMaxPercentAbstain = max(coalAbstain)
    coalMaxPercentAbsent = max(coalAbsent)

    out["for"]["maxCoal"]=coalMaxPercentFor
    idsMaxForCoal = numpy.array(idsForCoal)[numpy.where(numpy.array(coalFor) == coalMaxPercentFor)[0]]
    out["for"]["maxCoalID"] = list(idsMaxForCoal)

    out["against"]["maxCoal"]=coalMaxPercentAgainst
    idsMaxAgainstCoal = numpy.array(idsCoalAgainst)[numpy.where(numpy.array(coalAgainst) == coalMaxPercentAgainst)[0]]
    out["against"]["maxCoalID"] = list(idsMaxAgainstCoal)

    out["abstain"]["maxCoal"]=coalMaxPercentAbstain
    idsMaxAbstainCoal = numpy.array(idsCoalAbstain)[numpy.where(numpy.array(coalAbstain) == coalMaxPercentAbstain)[0]]
    out["abstain"]["maxCoalID"] = list(idsMaxAbstainCoal)

    out["absent"]["maxCoal"]=coalMaxPercentAbsent
    idsMaxAbsentCoal = numpy.array(idsCoalAbsent)[numpy.where(numpy.array(coalAbsent) == coalMaxPercentAbsent)[0]]
    out["absent"]["maxCoalID"] = list(idsMaxAbsentCoal)

    #Calculations for opozition
    #delete coalition groups from members in PGs
    map(membersInPGs.__delitem__, [str(coalitionIds) for coalitionIds in coalition['coalition']])
    idsForOpp, oppFor = zip(*[(member,float(sum(map(voteFor,votes[str(member)].values())))/float(len(votes[str(member)].values()))*100) for i in membersInPGs.keys() for member in membersInPGs[str(i)] if len(votes[str(member)].values()) > 0])
    idsOppAgainst, oppAgainst = zip(*[(member,float(sum(map(voteAgainst,votes[str(member)].values())))/float(len(votes[str(member)].values()))*100) for i in membersInPGs.keys() for member in membersInPGs[str(i)] if len(votes[str(member)].values()) > 0])
    idsOppAbstain, oppAbstain = zip(*[(member,float(sum(map(voteAbstain,votes[str(member)].values())))/float(len(votes[str(member)].values()))*100) for i in membersInPGs.keys() for member in membersInPGs[str(i)] if len(votes[str(member)].values()) > 0])
    idsOppAbsent, oppAbsent = zip(*[(member,float(sum(map(voteAbsent,votes[str(member)].values())))/float(len(votes[str(member)].values()))*100) for i in membersInPGs.keys() for member in membersInPGs[str(i)] if len(votes[str(member)].values()) > 0])
    oppMaxPercentFor = max(oppFor)
    oppMaxPercentAgainst = max(oppAgainst)
    oppMaxPercentAbstain = max(oppAbstain)
    oppMaxPercentAbsent = max(oppAbsent)

    out["for"]["maxOpp"]=oppMaxPercentFor

    memReq = getMPStaticPL(request, idsForOpp[oppFor.index(oppMaxPercentFor)])
    memberData = json.loads(memReq.content)
    idsMaxForOppo = numpy.array(idsForOpp)[numpy.where(numpy.array(oppFor) == oppMaxPercentFor)[0]]
    out["for"]["maxOppID"] = list(idsMaxForOppo)

    out["against"]["maxOpp"]=oppMaxPercentAgainst
    memReq = getMPStaticPL(request, idsOppAgainst[oppAgainst.index(oppMaxPercentAgainst)])
    memberData = json.loads(memReq.content)
    idsMaxAgainstOppo = numpy.array(idsOppAgainst)[numpy.where(numpy.array(oppAgainst) == oppMaxPercentAgainst)[0]]
    out["against"]["maxOppID"] = list(idsMaxAgainstOppo)

    out["abstain"]["maxOpp"]=oppMaxPercentAbstain

    memReq = getMPStaticPL(request, idsOppAbstain[oppAbstain.index(oppMaxPercentAbstain)])
    memberData = json.loads(memReq.content)
    idsMaxAbstainOppo = numpy.array(idsOppAbstain)[numpy.where(numpy.array(oppAbstain) == oppMaxPercentAbstain)[0]]
    out["abstain"]["maxOppID"] = list(idsMaxAbstainOppo)

    out["absent"]["maxOpp"]=oppMaxPercentAbsent
    idsMaxAbsentOppo = numpy.array(idsOppAbsent)[numpy.where(numpy.array(oppAbsent) == oppMaxPercentAbsent)[0]]
    out["absent"]["maxOppID"] = list(idsMaxAbsentOppo)

    final_response = saveOrAbortNew(
        CutVotes,
        created_for=date_of,
        person = Person.objects.get(id_parladata=person_id),
        this_for = out["for"]["this"],
        this_against = out["against"]["this"],
        this_abstain = out["abstain"]["this"],
        this_absent = out["absent"]["this"],
        coalition_for = coal_avg["for"],
        coalition_against = coal_avg["against"],
        coalition_abstain = coal_avg["abstain"],
        coalition_absent = coal_avg["absent"],
        coalition_for_max = out["for"]["maxCoal"],
        coalition_against_max = out["against"]["maxCoal"],
        coalition_abstain_max = out["abstain"]["maxCoal"],
        coalition_absent_max = out["absent"]["maxCoal"],
        coalition_for_max_person = ','.join(map(str, out["for"]["maxCoalID"])),
        coalition_against_max_person = ','.join(map(str, out["against"]["maxCoalID"])),
        coalition_abstain_max_person = ','.join(map(str, out["abstain"]["maxCoalID"])),
        coalition_absent_max_person = ','.join(map(str, out["absent"]["maxCoalID"])),
        opposition_for = oppo_avg["for"],
        opposition_against = oppo_avg["against"],
        opposition_abstain = oppo_avg["abstain"],
        opposition_absent= oppo_avg["absent"],
        opposition_for_max =out["for"]["maxOpp"],
        opposition_against_max = out["against"]["maxOpp"],
        opposition_abstain_max = out["abstain"]["maxOpp"],
        opposition_absent_max = out["absent"]["maxOpp"],
        opposition_for_max_person = ','.join(map(str, out["for"]["maxOppID"])),
        opposition_against_max_person = ','.join(map(str, out["against"]["maxOppID"])),
        opposition_abstain_max_person = ','.join(map(str, out["abstain"]["maxOppID"])),
        opposition_absent_max_person = ','.join(map(str, out["absent"]["maxOppID"]))
    )

    return JsonResponse(out)


def getCutVotes(request, person_id, date=None):
    cutVotes = getPersonCardModelNew(CutVotes, person_id, date)
    static = getPersonCardModelNew(MPStaticPL, person_id, date)

    out = {
        'person': getPersonData(person_id, date),
        'results': {
            'abstain': {
                'score': cutVotes.this_abstain,
                'maxCoalition': {
                    'mps': [getPersonData(textid, date) for textid in cutVotes.coalition_abstain_max_person.split(',')],
                    'score': cutVotes.coalition_abstain_max
                },
                'maxOpposition': {
                    'mps': [getPersonData(textid, date)  for textid in cutVotes.opposition_abstain_max_person.split(',')],
                    'score': cutVotes.opposition_abstain_max
                },
                "avgOpposition": {'score': cutVotes.opposition_abstain},
                "avgCoalition": {'score': cutVotes.coalition_abstain},
            },
            "against": {
                'score': cutVotes.this_against,
                'maxCoalition': {
                    'mps': [getPersonData(textid, date) for textid in cutVotes.coalition_against_max_person.split(',')],
                    'score': cutVotes.coalition_against_max
                },
                'maxOpposition': {
                    'mps': [getPersonData(textid, date) for textid in cutVotes.opposition_against_max_person.split(',')],
                    'score': cutVotes.opposition_against_max
                },
                "avgOpposition": {'score': cutVotes.opposition_against},
                "avgCoalition": {'score': cutVotes.coalition_against},
            },
            "absent": {
                'score': cutVotes.this_absent,
                'maxCoalition': {
                    'mps': [getPersonData(textid, date) for textid in cutVotes.coalition_absent_max_person.split(',')],
                    'score': cutVotes.coalition_absent_max
                },
                'maxOpposition': {
                    'mps': [getPersonData(textid, date) for textid in cutVotes.opposition_absent_max_person.split(',')],
                    'score': cutVotes.opposition_absent_max
                },
                "avgOpposition": {'score': cutVotes.opposition_absent},
                "avgCoalition": {'score': cutVotes.coalition_absent},
            },
            'for': {
                'score': cutVotes.this_for,
                'maxCoalition': {
                    'mps': [getPersonData(textid, date) for textid in cutVotes.coalition_for_max_person.split(',')],
                    'score': cutVotes.coalition_for_max
                },
                'maxOpposition': {
                    'mps': [getPersonData(textid, date) for textid in cutVotes.opposition_for_max_person.split(',')],
                    'score': cutVotes.opposition_for_max
                },
                "avgOpposition": {'score': cutVotes.opposition_for},
                "avgCoalition": {'score': cutVotes.coalition_for},
            },
        }
    }
    return JsonResponse(out)


#   conflicting change, in here for backup, remove after 14th of July 2015
#
#   for i in content.keys():
#       data[i] = [len(speech.split()) for speech in content[i]]
#
#   for i in data.keys():
#       allMPs[i] = sum(data[i])
#
#   thisMP = allMPs[id]
#   average = sum(allMPs.values()) / 90
#   maximumMP = max(allMPs.iterkeys(), key=(lambda key: allMPs[key]))
#   maximum = allMPs[maximumMP]
#
#   toDB = SpokenWords(person = Person.objects.get(id_parladata=id),
#                   maxMP = Person.objects.get(id_parladata=maximumMP),
#                   average = average,
#                   maximum = maximum
#                   )
#   #toDB.save()
#
#   return JsonResponse(allMPs)

def setStyleScoresALLShell():

    mps = requests.get(API_URL+'/getMPs/').json()
    print 'Starting average scores'
    average_scores = makeAverageStyleScores()

    print 'Ending average scores'

    print 'Starting MPs'
    for mp in mps:

        person_id = mp['id']

        print 'MP id: ' + str(person_id)

#        # get speeches of MP
#        speeches = requests.get(API_URL+'/getSpeeches/' + person_id).json()
#        speeches_content = [speech['content'] for speech in speeches]
#        speeches_megastring = string.join(speeches_content)
#
#        # count total words
#        counter = Counter()
#        counter = countWords(speeches_megastring, counter)
#        total = sum(counter.values())

        # get word counts with solr
        counter = Counter(getCountList(int(person_id)))
        total = sum(counter.values())

        scores_local = getScores([problematicno, privzdignjeno, preprosto], counter, total)

        average = average_scores

        print scores_local, average

        saveOrAbort(
            model=StyleScores,
            person=Person.objects.get(id_parladata=int(person_id)),
            problematicno=scores_local['problematicno'],
            privzdignjeno=scores_local['privzdignjeno'],
            preprosto=scores_local['preprosto'],
            problematicno_average=average['problematicno'],
            privzdignjeno_average=average['privzdignjeno'],
            preprosto_average=average['preprosto']
        )

    return HttpResponse('All MPs updated');


def setStyleScoresALL(request):

    mps = requests.get(API_URL+'/getMPs/').json()
    print 'Starting average scores'
    average_scores = makeAverageStyleScores()

    print 'Ending average scores'

    print 'Starting MPs'
    for mp in mps:

        person_id = mp['id']

        print 'MP id: ' + str(person_id)

#        # get speeches of MP
#        speeches = requests.get(API_URL+'/getSpeeches/' + person_id).json()
#        speeches_content = [speech['content'] for speech in speeches]
#        speeches_megastring = string.join(speeches_content)
#
#        # count total words
#        counter = Counter()
#        counter = countWords(speeches_megastring, counter)
#        total = sum(counter.values())

        # get word counts with solr
        counter = Counter(getCountList(int(person_id)))
        total = sum(counter.values())

        scores_local = getScores([problematicno, privzdignjeno, preprosto], counter, total)

        average = average_scores

        print scores_local, average

        saveOrAbort(
            model=StyleScores,
            person=Person.objects.get(id_parladata=int(person_id)),
            problematicno=scores_local['problematicno'],
            privzdignjeno=scores_local['privzdignjeno'],
            preprosto=scores_local['preprosto'],
            problematicno_average=average['problematicno'],
            privzdignjeno_average=average['privzdignjeno'],
            preprosto_average=average['preprosto']
        )

    return HttpResponse('All MPs updated');

def setStyleScores(request, person_id):
    speeches = requests.get(API_URL+'/getSpeeches/' + person_id).json()
    speeches_content = [speech['content'] for speech in speeches]
    speeches_megastring = string.join(speeches_content)

    average_scores = makeAverageStyleScores()

    counter = Counter()
    counter = countWords(speeches_megastring, counter)
    total = sum(counter.values())

    problematicno_local = getScore(problematicno, counter, total),
    privzdignjeno_local = getScore(privzdignjeno, counter, total),
    preprosto_local = getScore(preprosto, counter, total),
    average = average_scores

    print problematicno_local[0], privzdignjeno_local[0], preprosto_local[0], average

    result = saveOrAbort(model=StyleScores, person=Person.objects.get(id_parladata=int(person_id)), problematicno=problematicno_local[0], privzdignjeno=privzdignjeno_local[0], preprosto=preprosto_local[0], problematicno_average=average['problematicno'], privzdignjeno_average=average['privzdignjeno'], preprosto_average=average['preprosto'])

    if result:
        return HttpResponse('All iz well')

    else:
        return HttpResponse('All was well');



    return JsonResponse(output, safe=False)

def getStyleScores(request, person_id, date=None):
    card = getPersonCardModel(StyleScores, int(person_id), date)

    out = {
        'person': getPersonData(person_id, date),
        'results': {
            'privzdignjeno': card.privzdignjeno,
            'problematicno': card.problematicno,
            'preprosto': card.preprosto,
            'average': {
                'privzdignjeno_average': card.privzdignjeno_average,
                'problematicno_average': card.problematicno_average,
                'preprosto_average': card.preprosto_average
            }
        }
    }

    return JsonResponse(out, safe=False)

def getTotalStyleScores(request):
#    speeches = requests.get(API_URL+'/getAllSpeeches/').json()
#    speeches_content = [speech['content'] for speech in speeches]
#    speeches_megastring = string.join(speeches_content)
#
#    counter = Counter()
#    counter = countWords(speeches_megastring, counter)
#    total = sum(counter.values())

    data = requests.get('http://parlameter.si:8983/solr/knedl/admin/luke?fl=content_t&numTerms=200000&wt=json').json()

    wordlist = data['fields']['content_t']['topTerms']

    wordlist_new = {}
    i = 0
    limit = len(wordlist)/2

    while i < limit:

        if wordlist[i + 1] > 0:
            wordlist_new[wordlist[i]] = wordlist[i + 1]
        else:
            break

        i = i + 2

    counter = Counter(wordlist_new)
    total = sum(counter.values())

    output = getScores([problematicno, privzdignjeno, preprosto], counter, total)
#    output = {'problematicno': getScore(problematicno, counter, total),
#              'privzdignjeno': getScore(privzdignjeno, counter, total),
#              'preprosto': getScore(preprosto, counter, total),
##              'total': total
#             }

    return JsonResponse(output, safe=False)

def makeAverageStyleScores():
#    speeches = requests.get(API_URL+'/getAllSpeeches/').json()
#    speeches_content = [speech['content'] for speech in speeches]
#    speeches_megastring = string.join(speeches_content)

    data = requests.get('http://parlameter.si:8983/solr/knedl/admin/luke?fl=content_t&numTerms=200000&wt=json').json()

    wordlist = data['fields']['content_t']['topTerms']

    wordlist_new = {}
    i = 0
    limit = len(wordlist)/2

    while i < limit:

        if wordlist[i + 1] > 0:
            wordlist_new[wordlist[i]] = wordlist[i + 1]
        else:
            break

        i = i + 2

    counter = Counter(wordlist_new)
#    counter = countWords(speeches_megastring, counter)
    total = sum(counter.values())
    print total

    output = getScores([problematicno, privzdignjeno, preprosto], counter, total)

#    output = {'problematicno': getScore(problematicno, counter, total),
#              'privzdignjeno': getScore(privzdignjeno, counter, total),
#              'preprosto': getScore(preprosto, counter, total),
#             }

    return output

def setTFIDF(request, person_id):

    mps = requests.get(API_URL+'/getMPs/').json()

    person = Person.objects.get(id_parladata=int(person_id))

    mp_ids = [mp['id'] for mp in mps]

    speeches_grouped = [{'person_id': mp, 'speeches': requests.get(API_URL+'/getSpeeches/' + str(mp)).json()} for mp in mp_ids]

    tfidf = TFIDF(speeches_grouped, person_id)

    print tfidf[:10]

    newtfidf = []
    for i, term in enumerate(tfidf[:10]):
        term['rank'] = i + 1
        newtfidf.append(term)

    if saveOrAbort(Tfidf, person=person, data=newtfidf):

        return HttpResponse('All iz well')

    else:
        return HttpResponse('All waz well');

def getTFIDF(request, person_id, date=None):

    card = getPersonCardModel(Tfidf, int(person_id), date)

    out = {
        'person': getPersonData(person_id, date),
        'results': card.data
    }

    return JsonResponse(out)

def setVocabularySizeAndSpokenWords(request, date_=None):
    sw = WordAnalysis(API_URL, date_)

    #Vocabolary size
    all_score = sw.getVocabularySize()
    max_score, maxMPid = sw.getMaxVocabularySize()
    avg_score = sw.getAvgVocabularySize()
    date_of = sw.getDate()
    maxMP = Person.objects.get(id_parladata=maxMPid)

    print "[INFO] saving vocabulary size"
    for p in all_score:
        saveOrAbortNew(model=VocabularySize,
                       person=Person.objects.get(id_parladata=int(p['person_id'])),
                       created_for=date_of,
                       score=int(p['coef']),
                       maxMP=maxMP,
                       average=avg_score,
                       maximum=max_score)
    #Spoken words
    all_words = sw.getSpokenWords()
    max_words, maxWordsMPid = sw.getMaxSpokenWords()
    avgSpokenWords = sw.getAvgSpokenWords()
    date_of = sw.getDate()
    maxMP = Person.objects.get(id_parladata=maxWordsMPid)

    print "[INFO] saving spoken words"
    for p in all_words:
        saveOrAbortNew(model=SpokenWords,
                       created_for=date_of,
                       person=Person.objects.get(id_parladata=int(p['person_id'])),
                       score=int(p['wordcount']),
                       maxMP=maxMP,
                       average=avgSpokenWords,
                       maximum=max_words)

    return HttpResponse('All MPs updated.')

#Depricated
def setVocabularySizeALL(request, date_):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()
        date_=""

#    thisperson = Person.objects.get(id_parladata=int(person_id))

    mps = requests.get(API_URL+'/getMPs/'+date_).json()

    vocabulary_sizes = []
    result = {}

    for mp in mps:

        speeches = requests.get(API_URL+'/getSpeeches/' + str(mp['id']) + ("/"+date_) if date_ else "").json()

        text = ''.join([speech['content'] for speech in speeches])

        vocabulary_sizes.append({'person_id': mp['id'], 'vocabulary_size': len(countWords(text, Counter()))})

#        if int(mp['id']) == int(person_id):
#            result['person'] = len(countWords(text, Counter()))

    vocabularies_sorted = sorted(vocabulary_sizes, key=lambda k: k['vocabulary_size'])

    scores = [person['vocabulary_size'] for person in vocabulary_sizes]

    result['average'] = float(sum(scores))/float(len(scores))

    result['max'] = vocabularies_sorted[-1]['vocabulary_size']
    maxMP = Person.objects.get(id_parladata=vocabularies_sorted[-1]['person_id'])

#    result.append({'person_id': vocabularies_sorted[-1]['person_id'], 'vocabulary_size': vocabularies_sorted[-1]['vocabulary_size']})

    for p in vocabularies_sorted:
        saveOrAbortNew(
            VocabularySize,
            person=Person.objects.get(id_parladata=int(p['person_id'])),
            created_for=date_of,
            score=[v['vocabulary_size'] for v in vocabularies_sorted if v['person_id'] == p['person_id']][0],
            maxMP=maxMP,
            average=result['average'],
            maximum=result['max'])

    return HttpResponse('All MPs updated.')

#    if saveOrAbort(VocabularySize, person=thisperson, score=result['person'], maxMP=maxMP, average=result['average'], maximum=result['max']):
#        return HttpResponse('All iz well')
#    else:
#        return HttpResponse('All was well')
#
#    result_ = saveOrAbort(model=VocabularySize, person=Person.objects.get(id_parladata=int(person_id)), this_person=result[0]['vocabulary_size'], maxMP=Person.objects.get(id_parladata=int(vocabularies_sorted[-1]['person_id'])), average=float(sum(scores))/float(len(scores)), maximum=vocabularies_sorted[-1]['vocabulary_size'])
#
#    return JsonResponse(result, safe=False)

def setVocabularySize(request, person_id, date_=None):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = findDatesFromLastCard(VocabularySize, person_id, datetime.now().strftime(API_DATE_FORMAT))[0]
        date_=""

    thisperson = Person.objects.get(id_parladata=int(person_id))

    mps = requests.get(API_URL+'/getMPs/'+date_).json()

    vocabulary_sizes = []
    result = {}

    for mp in mps:

        speeches = requests.get(API_URL+'/getSpeeches/'+date_ + str(mp['id'])).json()

        text = ''.join([speech['content'] for speech in speeches])

        vocabulary_sizes.append({'person_id': mp['id'], 'vocabulary_size': len(countWords(text, Counter()))})

        if int(mp['id']) == int(person_id):
            result['person'] = len(countWords(text, Counter()))

    vocabularies_sorted = sorted(vocabulary_sizes, key=lambda k: k['vocabulary_size'])

    scores = [person['vocabulary_size'] for person in vocabulary_sizes]

    result['average'] = float(sum(scores))/float(len(scores))

    result['max'] = vocabularies_sorted[-1]['vocabulary_size']
    maxMP = Person.objects.get(id_parladata=vocabularies_sorted[-1]['person_id'])

#    result.append({'person_id': vocabularies_sorted[-1]['person_id'], 'vocabulary_size': vocabularies_sorted[-1]['vocabulary_size']})

#    for p in vocabularies_sorted:
#        saveOrAbort(
#            VocabularySize,
#            person=Person.objects.get(id_parladata=int(p['person_id'])),
#            score=[v['vocabulary_size'] for v in vocabularies_sorted if v['person_id'] == p['person_id']][0],
#            maxMP=maxMP,
#            average=result['average'],
#            maximum=result['max'])
#
#    return HttpResponse('All MPs updated.')

    if saveOrAbortNew(VocabularySize,
                      person=thisperson,
                      created_for=date_of,
                      score=result['person'],
                      maxMP=maxMP,
                      average=result['average'],
                      maximum=result['max']):
        return HttpResponse('All iz well')
    else:
        return HttpResponse('All was well')


def getVocabularySize(request, person_id, date_=None):

    card = getPersonCardModelNew(VocabularySize, person_id, date_)

    out = {
        'person': getPersonData(person_id, date_),
        'results': {
            'max': {
                'score': card.maximum,
                'mps': [getPersonData(card.maxMP.id_parladata, date_)]
            },
            'average': card.average,
            'score': card.score
        }
    }

    return JsonResponse(out, safe=False)


def getVocabolarySizeLanding(request, date_=None):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        person_id=None
        date_of = VocabularySize.objects.all().order_by("-created_for")[0].created_for
        date_ = date_of.strftime(API_DATE_FORMAT)
    mps = requests.get(API_URL+'/getMPs/'+date_).json()
    datas = [getPersonCardModelNew(VocabularySize, mp["id"], date_) for mp in mps]
    print datas
    return JsonResponse(sorted([{"person": getPersonData(data.person.id_parladata, date_), "score": data.score} for data in datas], key=lambda k: k['score']), safe=False)


#just method ALL is edited for date
def setAverageNumberOfSpeechesPerSession(request, person_id):

    person = Person.objects.get(id_parladata=int(person_id))
    speeches = requests.get(API_URL+'/getSpeechesOfMP/' + person_id).json()
    no_of_speeches = len(speeches)

    # fix for "Dajem besedo"
    #no_of_speeches = no_of_speeches - int(requests.get(API_URL + '/getNumberOfFormalSpeeches/' + person_id))

    no_of_sessions = requests.get(API_URL+ '/getNumberOfPersonsSessions/' + person_id).json()['sessions_with_speech']

    score = no_of_speeches/no_of_sessions

    mps = requests.get(API_URL+'/getMPs/').json()
    mp_scores = []

    for mp in mps:
        mp_no_of_speeches = len(requests.get(API_URL+'/getSpeechesOfMP/' + str(mp['id'])).json())

        mp_no_of_sessions = requests.get(API_URL+ '/getNumberOfPersonsSessions/' + str(mp['id'])).json()['sessions_with_speech']

        mp_scores.append({'id': mp['id'], 'score': mp_no_of_speeches/mp_no_of_sessions})


    mp_scores_sorted = sorted(mp_scores, key=lambda k: k['score'])

    average = sum([mp['score'] for mp in mp_scores])/len(mp_scores)

    saveOrAbort(model=AverageNumberOfSpeechesPerSession, person=person, score=score, average=average, maximum=mp_scores_sorted[-1]['score'], maxMP=Person.objects.get(id_parladata=int(mp['id'])))

    return HttpResponse('All iz well')

def setAverageNumberOfSpeechesPerSessionAll(request, date_=None):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = findDatesFromLastCard(Presence, person_id, datetime.now().date())[0]
        date_=""

    mps = requests.get(API_URL+'/getMPs/'+date_).json()
    mp_scores = []

    for mp in mps:
        mp_no_of_speeches = len(requests.get(API_URL+'/getSpeechesOfMP/' + str(mp['id'])  + ("/"+date_) if date_ else "").json())

        # fix for "Dajem besedo"
        #mp_no_of_speeches = mp_no_of_speeches - int(requests.get(API_URL + '/getNumberOfFormalSpeeches/' + str(mp['id']) + ("/"+date_) if date_ else "").text)

        mp_no_of_sessions = requests.get(API_URL+ '/getNumberOfPersonsSessions/' + str(mp['id']) + ("/"+date_) if date_ else "").json()['sessions_with_speech']

        if mp_no_of_sessions > 0:
            mp_scores.append({'id': mp['id'], 'score': mp_no_of_speeches/mp_no_of_sessions})
        else:
            mp_scores.append({'id': mp['id'], 'score': 0})


    mp_scores_sorted = sorted(mp_scores, key=lambda k: k['score'])

    average = sum([mp['score'] for mp in mp_scores])/len(mp_scores)

    for mp in mp_scores_sorted:
        person = Person.objects.get(id_parladata=int(mp['id']))
        score = mp['score']


        saveOrAbortNew(
            model=AverageNumberOfSpeechesPerSession,
            created_for=date_of,
            person=person,
            score=score,
            average=average,
            maximum=mp_scores_sorted[-1]['score'],
            maxMP=Person.objects.get(id_parladata=int(mp_scores_sorted[-1]['id'])))

    return HttpResponse('All iz well')

def getAverageNumberOfSpeechesPerSession(request, person_id, date=None):

    card = getPersonCardModelNew(AverageNumberOfSpeechesPerSession, person_id, date)
    #static = getPersonCardModelNew(MPStaticPL, person_id, date)

    out = {
        'person': getPersonData(person_id, date),
        'results': {
            'max': {
                'score': card.maximum,
                'mps': [getPersonData(card.maxMP.id_parladata, date)]
            },
            'average': card.average,
            'score': card.score
        }
    }

    return JsonResponse(out, safe=False)


# get MPs IDs
def getMPsIDs(request):
    output = []
    data = requests.get(API_URL+'/getMPs/')
    data = data.json()

    output = {"list": [i['id'] for i in data], "lastDate": Session.objects.all().order_by("-start_time")[0].start_time.strftime(API_DATE_FORMAT)}

    return JsonResponse(output, safe=False)


def runSetters(request, date_to):
    toDate = datetime.strptime(date_to, API_DATE_FORMAT).date()
    setters_models = {
        #model: setter,
        # not working yet #LastActivity: BASE_URL+'/p/setLastActivity/',
        # CutVotes: setCutVotes,#BASE_URL+'/p/setCutVotes/',

        MPStaticPL: setMPStaticPL,
        #MembershipsOfMember: setMembershipsOfMember,
        #LessEqualVoters: setLessEqualVoters,
        #EqualVoters: setMostEqualVoters,
        #Presence: setPercentOFAttendedSession,
    }
    memberships = requests.get(API_URL+'/getAllTimeMemberships').json()
    IDs = getIDs()
    # print IDs
    allIds = len(IDs)
    curentId = 0
    for membership in memberships:
        if membership["end_time"]:
            end_time = datetime.strptime(membership["end_time"].split("T")[0],"%Y-%m-%d").date()
            if end_time>toDate:
                end_time=toDate
        else:
            end_time=toDate

        for model, setter in setters_models.items():
            print setter, date_to
            if membership["start_time"]:
                print "START",membership["start_time"]
                start_time = datetime.strptime(membership["start_time"].split("T")[0],"%Y-%m-%d")
                dates = findDatesFromLastCard(model, membership["id"], end_time.strftime(API_DATE_FORMAT), start_time.strftime(API_DATE_FORMAT))
            else:
                dates = findDatesFromLastCard(model, membership["id"], end_time.strftime(API_DATE_FORMAT))
            for date in dates:
                print date.strftime('%d.%m.%Y')
                print str(membership["id"]) + "/" + date.strftime('%d.%m.%Y')
                setter(request, str(membership["id"]), date.strftime('%d.%m.%Y'))

                #if setter == setMPStaticPL: # Prevent that runner doesn't waste time with ... Which doesn't change often
                #    break;
        #setLastActivity allways runs without date
        #setLastActivity(request, str(membership["id"]))
        curentId += 1
                # result = requests.get(setter + str(ID) + "/" + date.strftime('%d.%m.%Y')).status_code

    #Runner for setters ALL
    all_in_one_setters_models = {
        #AverageNumberOfSpeechesPerSession: setAverageNumberOfSpeechesPerSessionAll,
        #VocabularySize: setVocabularySizeAndSpokenWords,
        #Compass: setCompass,
    }

    zero=datetime(day=2, month=8, year=2014).date()
    for model, setter in all_in_one_setters_models.items():
        print (toDate-datetime(day=2, month=8, year=2014).date()).days
        for i in range((toDate-datetime(day=2, month=8, year=2014).date()).days):
            print (zero+timedelta(days=i)).strftime('%d.%m.%Y')
            setter(request, (zero+timedelta(days=i)).strftime('%d.%m.%Y'))

    return JsonResponse({"status": "all is fine :D"}, safe=False)


#Create all cards for data_ date. If date_ is None set for run setters for today.
def onDateCardRunner(request, date_=None):
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()
        date_ = date_of.strftime(API_DATE_FORMAT)
    setters = [
        setCutVotes,
        setMPStaticPL,
        setMembershipsOfMember,
        setLessEqualVoters,
        setMostEqualVoters,
        setPercentOFAttendedSession,
    ]

    memberships = requests.get(API_URL+'/getMPs/'+date_).json()
    IDs = getIDs()
    # print IDs
    allIds = len(IDs)
    curentId = 0
    for membership in memberships:
        for setter in setters:
            print "running:" + str(setter)
            try:
                setter(request, str(membership["id"]), date_)
            except:
                print FAIL + "FAIL on: " + str(setter) + " and with id: " + str(membership["id"]) + ENDC
        setLastActivity(request, str(membership["id"]))

    #Runner for setters ALL
    all_in_one_setters = [
        setAverageNumberOfSpeechesPerSessionAll,
        setVocabularySizeAndSpokenWords,
        setCompass,
    ]

    zero=datetime(day=2, month=8, year=2014).date()
    for setter in all_in_one_setters:
        print "running:" + str(setter)
        try:
            setter(request, date_)
        except:
            print "FAIL on: " + str(setter)

def setCompass(request, date_=None):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()
        date_=""

    data = notes.getData(date_of)
    if data == []:
        return JsonResponse({"status": "no data"})
    print data
    existing_compas = Compass.objects.filter(created_for=date_of)
    if existing_compas:
        existing_compas[0].data = data
        existing_compas[0].save()
    else:
        Compass(created_for=date_of,
                data=data).save()

    JsonResponse({"status": 'All iz well'})

def getCompass(request, date_=None): # TODO make propper setters and getters
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()
        date_=""
    data = Compass.objects.all().order_by('created_for')[0].data

    return JsonResponse(data, safe=False)

def setTaggedBallots(request, person_id):

    person = Person.objects.get(id_parladata=int(person_id))
    data = requests.get(API_URL + '/getTaggedVotes/' + str(person_id)).json()

    tagged_ballots = TaggedBallots(person=person, data=data)
    tagged_ballots.save()

    return HttpResponse('All iz well')

def getTaggedBallots_(request, person_id, date=None):

    card = getPersonCardModel(TaggedBallots, person_id, date)
    static = getPersonCardModelNew(MPStaticPL, person_id, date)

    out = {
        'person': getPersonData(person_id, date),
        'ballots': card.data
    }

    return JsonResponse(out, safe=False)


def setMembershipsOfMember(request, person_id, date=None):
    if date:
        #call parladata api with date, maybe you will need to fix parladata api call
        data = requests.get(API_URL+'/getMembershipsOfMember/' + person_id + "/" + date).json()
        #date_of is date for created_for which is atribute of model (you also need to add created_for in model)
        date_of = datetime.strptime(date, API_DATE_FORMAT)
    else:
        data = requests.get(API_URL+'/getMembershipsOfMember/'+ person_id).json()
        date_of = datetime.now().date()

    person = Person.objects.get(id_parladata=int(person_id))

    memberships = saveOrAbortNew(MembershipsOfMember, created_for=date_of, person=person, data=data)

    return HttpResponse(memberships)


def getMembershipsOfMember(request, person_id, date=None):
    card = getPersonCardModelNew(MembershipsOfMember, person_id, date)
    static = getPersonCardModelNew(MPStaticPL, person_id, date)

    out = {
        'person': getPersonData(person_id, date),
        'memberships': card.data
    }

    return JsonResponse(out, safe=False)


def getTaggedBallots(request, person_id, date_=None):
    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT)
    else:
        date_of = datetime.now().date()
    out = []
    ballots = Ballot.objects.filter(person__id_parladata=person_id, start_time__lte=date_of)
    ballots = [[ballot for ballot in ballots.filter(start_time__range=[t_date, t_date+timedelta(days=1)])] for t_date in ballots.order_by("start_time").datetimes('start_time', 'day')]
    for day in ballots:
        dayData = {"date": day[0].start_time.strftime(API_OUT_DATE_FORMAT), "ballots":[]}
        for ballot in day:
            dayData["ballots"].append({
                "motion": ballot.vote.motion,
                "ballot_id": ballot.id_parladata,
                "session_id": ballot.vote.session.id_parladata if ballot.vote.session else None,
                "option": ballot.option,
                "tags": ballot.vote.tags})
        out.append(dayData)


    tags = list(Tag.objects.all().values_list("name", flat=True))
    result  = {
        'person': getPersonData(person_id, date_),
        'all_tags': tags,
        'results': list(reversed(out))
        }
    return JsonResponse(result, safe=False)
