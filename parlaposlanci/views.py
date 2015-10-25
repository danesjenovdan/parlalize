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
from kvalifikatorji.scripts import numberOfWords, countWords, getScore, problematicno, privzdignjeno, preprosto, TFIDF
from collections import Counter
from parlalize.settings import LAST_ACTIVITY_COUNT
from .models import *
from parlalize.settings import API_URL

# Create your views here.

#get List of MPs
def getMPsList(request):
    output = []
    data = requests.get(API_URL+'/getMPs/')
    data = data.json()

    output = [{'id': i['id'], 'image': i['image'], 'name': i['name'], 'membership': i['membership'], 'acronym': i['acronym'], 'district': i['district']} for i in data]

    return JsonResponse(output, safe=False)


##returns MP static data like PoliticalParty, age, ....
def setMPStaticPL(request, person_id):
    dic = dict()
    data = requests.get(API_URL+'/getMPStatic/'+str(person_id)+'/').json()

    result = saveOrAbort(model=MPStaticPL, person=Person.objects.get(id_parladata=int(person_id)), voters=data['voters'], age=data['age'], mandates=data['mandates'], party_id=data['party_id'], education=data['education'], previous_occupation=data['previous_occupation'], name=data['name'], district=data['district'], facebook=data['social']['facebook'], twitter=data['social']['twitter'], linkedin=data['social']['linkedin'], party_name=data['party'], acronym=data['acronym'])

    if result:
        for group in data['groups']:
            new_group = MPStaticGroup(person=MPStaticPL.objects.filter(person__id_parladata=int(person_id)).latest('created_at'), groupid=int(group['id']), groupname=group['name'])
            new_group.save()

    return HttpResponse('All iz well')


def getMPStaticPL(request, person_id, date=None):
    card = getPersonCardModel(MPStaticPL, person_id, date)

    if card.twitter == 'False': print card.twitter

    data = {
        'person': {
            'name': Person.objects.get(id_parladata=int(person_id)).name,
            'id': int(person_id)
        },
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
def setPercentOFAttendedSession(request, person_id):
    data = {}
    number = requests.get(API_URL+'/getNumberOfAllMPAttendedSessions/')
    sessions =  requests.get(API_URL+'/getSessions/')
    sessions = sessions.json()
    number = number.json()

    data = {i:number[i]*100 / len(sessions) for i in number.keys()}

    thisMP = data[person_id]
    maximumMP = max(data.iterkeys(), key=(lambda key: data[key])) #kaj ce jih je vec z isto vrednostjo
    average = sum(data.values()) / 90
    maximum = data[maximumMP]

    result = saveOrAbort(model=Presence, person=Person.objects.get(id_parladata=int(person_id)), person_value=thisMP, maxMP=Person.objects.get(id_parladata=int(maximumMP)), average=average, maximum=maximum)

    return JsonResponse({'alliswell': result})

def getPercentOFAttendedSession(request, person_id, date=None):
	equalVoters = getPersonCardModel(Presence, person_id, date)

	out  = {
        'person': {
            "name": equalVoters.person.name,
            "id": equalVoters.person.id_parladata,
        },
		'results': {
            "value": equalVoters.person_value,
            "average": equalVoters.average,
            "max": {
                "name": equalVoters.maxMP.name,
                "id": equalVoters.maxMP.id_parladata,
                "value": equalVoters.maximum,
            }
        }
    }
	return JsonResponse(out)


#Saves to DB number of spoken word of MP and maximum and average of spoken words
def setNumberOfSpokenWordsALL(request):
    mps = requests.get(API_URL+'/getMPs/').json()

    mp_results = []

    for mp in mps:
        speeches = requests.get(API_URL+'/getSpeeches/' + str(mp['id'])).json()

        text = ''.join([speech['content'] for speech in speeches])

        mp_results.append({'person_id': mp['id'], 'wordcount': numberOfWords(text)})

    mps_sorted = sorted(mp_results, key=lambda k: k['wordcount'])

    all_speeches = requests.get(API_URL+'/getAllSpeeches/').json()
    text = ''.join([speech['content'] for speech in all_speeches])

    total_words = numberOfWords(text)
    average_words = total_words/len(mps)

    for result in mp_results:
        print result
        print '##################'
        print saveOrAbort(model=SpokenWords, person=Person.objects.get(id_parladata=int(result['person_id'])), score=int(result['wordcount']), maxMP=Person.objects.get(id_parladata=int(mps_sorted[-1]['person_id'])), average=average_words, maximum=mps_sorted[-1]['wordcount'])

    return HttpResponse('All iz well')

def getNumberOfSpokenWords(request, person_id, date=None):

    card = getPersonCardModel(SpokenWords, person_id, date)

    results = {
        'person': {
            'id': int(person_id),
            'name': Person.objects.get(id_parladata=int(person_id)).name
        },
        'results': {
            'score': card.score,
            'average': card.average,
            'max': {
                'id': card.maxMP.id_parladata,
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
            print acti.id_parladata
            if type(acti) == Speech:
                print "Speech"
                avtivity_ids.append(acti.id_parladata)
                types.append("speech")
                vote_name.append(acti.session.name)
                result.append("None")
                options.append("None")
                sessions.append(str(acti.session.id))
            else:
                print "Ballot"
                avtivity_ids.append(acti.vote.id_parladata)
                types.append("ballot")
                vote_name.append(acti.vote.motion)
                result.append(acti.vote.result)
                options.append(acti.option)
                sessions.append("None")

        out.append(saveOrAbort(model=LastActivity, person=Person.objects.get(id_parladata=int(person_id)), date=date, activity_id=";".join(map(str, avtivity_ids)), option=";".join(map(str, options)), result=";".join(map(str, result)), vote_name=";".join(vote_name), typee=";".join(types), session_id=";".join(sessions)))

    return JsonResponse(out, safe=False)

def getLastActivity(request, person_id, date=None):
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
                    "result": Vote.objects.get(id_parladata=activity_ids[i]).result,
                    "vote_name": vote_names[i],
                    "vote_id": int(activity_ids[i]),
                    "type": types[i],
                    "session_id": Vote.objects.get(id_parladata=int(activity_ids[i])).session.id
                    })
            elif types[i] == "speech":
                data.append({
                    "speech_id": int(activity_ids[i]),
                    "type": types[i],
                    "session_name": vote_names[i],
                    "session_id": sessions_ids[i]
                    })
        return {"date": str(day_activites.date.date()), "events": data}

    out = []
    equalVoters = getPersonCardModel(LastActivity, person_id, date)
    out.append(parseDayActivites(equalVoters))
    for i in range(LAST_ACTIVITY_COUNT - 1):
        startDate = equalVoters.date - timedelta(days=1)
        equalVoters = getPersonCardModel(LastActivity, person_id, datetime.strftime(startDate, "%d.%m.%Y"))
        if equalVoters == None:
            break;
        out.append(parseDayActivites(equalVoters))
    result  = {
        'person': {
            "name": equalVoters.person.name,
            "id": equalVoters.person.id_parladata,
        },
        'results': out
        }
    return JsonResponse(result, safe=False)

#TODO date
def getAllSpeeches(request, person_id, date=None):
    speeches = Speech.objects.filter(person__id_parladata=person_id)
    if date:
        print date
        speeches = [[speech for speech in speeches.filter(start_time__range=[date, date+timedelta(days=1)])] for date in speeches.filter(start_time__lte=datetime.strptime(date, '%d.%m.%Y')).order_by("start_time").datetimes('start_time', 'day')]
    else:
        speeches = [[speech for speech in speeches.filter(start_time__range=[date, date+timedelta(days=1)])] for date in speeches.order_by("start_time").datetimes('start_time', 'day')]
    out = []
    for day in speeches:
        dayData = {"date": str(day[0].start_time.date()), "speeches":[]}
        for speech in day:
            dayData["speeches"].append({
                "session_name": speech.session.name,
                "speech_id": speech.id_parladata,
                "session_id": speech.session.id_parladata})
        out.append(dayData)



    result  = {
        'person': {
            "name": Person.objects.get(id_parladata=person_id).name,
            "id": person_id,
        },
        'results': out
        }
    return JsonResponse(result, safe=False)


#method returns percent, how similar does the members vote
def getEqualVoters(request, id):
	votes = getLogicVotes()

	members = getMPsList(request)
	membersDict = {str(mp['id']):mp for mp in json.loads(members.content)}

	out = {vote:pearsonr(votes[str(id)].values(), votes[str(vote)].values())[0] for vote in sorted(votes.keys())}
	keys = sorted(out, key=out.get)

	for key in keys:
		membersDict[key].update({'ratio':out[str(key)]})
		membersDict[key].update({'id':key})
	return membersDict, keys

#Method return json with most similar voters to this voter
def setMostEqualVoters(request, person_id):
	members, keys = getEqualVoters(request, person_id)
	out = {index:members[key] for key, index in zip(keys[-6:-1], [5,4,3,2,1])}

	result = saveOrAbort(model=EqualVoters, person=Person.objects.get(id_parladata=int(person_id)), person1=Person.objects.get(id_parladata=int(out[1]['id'])), votes1=out[1]['ratio'], person2=Person.objects.get(id_parladata=int(out[2]['id'])), votes2=out[2]['ratio'], person3=Person.objects.get(id_parladata=int(out[3]['id'])), votes3=out[3]['ratio'], person4=Person.objects.get(id_parladata=int(out[4]['id'])), votes4=out[4]['ratio'], person5=Person.objects.get(id_parladata=int(out[5]['id'])), votes5=out[5]['ratio'])
	return HttpResponse('All iz well')

def getMostEqualVoters(request, person_id, date=None):
    equalVoters = getPersonCardModel(EqualVoters, person_id, date)

    print equalVoters.person1.id_parladata

    out = {
        'person': {
            'name': Person.objects.get(id_parladata=int(person_id)).name,
            'id': int(person_id)
        },
        'results': [
            {
                "ratio": equalVoters.votes1,
                "id": equalVoters.person1.id_parladata,
                "name": equalVoters.person1.name,
                "party": requests.get(API_URL+'/getMPParty/' + str(equalVoters.person1.id_parladata)).json(),
            },
            {
                "ratio": equalVoters.votes2,
                "id": equalVoters.person2.id_parladata,
                "name": equalVoters.person2.name,
                "party": requests.get(API_URL+'/getMPParty/' + str(equalVoters.person2.id_parladata) + '/').json(),
            },
            {
                "ratio": equalVoters.votes3,
                "id": equalVoters.person3.id_parladata,
                "name": equalVoters.person3.name,
                "party": requests.get(API_URL+'/getMPParty/' + str(equalVoters.person3.id_parladata) + '/').json(),
            },
            {
                "ratio": equalVoters.votes4,
                "id": equalVoters.person4.id_parladata,
                "name": equalVoters.person4.name,
                "party": requests.get(API_URL+'/getMPParty/' + str(equalVoters.person4.id_parladata) + '/').json(),
            },
            {
                "ratio": equalVoters.votes5,
                "id": equalVoters.person5.id_parladata,
                "name": equalVoters.person5.name,
                "party": requests.get(API_URL+'/getMPParty/' + str(equalVoters.person5.id_parladata) + '/').json(),
            }
        ]
    }

	#data = getPersonCardModel(EqualVoters, person_id)
    return JsonResponse(out, safe=False)

#Method return json with less similar voters to this voter
def setLessEqualVoters(request, person_id):
    members, keys = getEqualVoters(request, person_id)
    out = {index:members[key] for key, index in zip(keys[:5], [1,2,3,4,5])}

    result = saveOrAbort(model=LessEqualVoters, person=Person.objects.get(id_parladata=int(person_id)), person1=Person.objects.get(id_parladata=int(out[1]['id'])), votes1=out[1]['ratio'], person2=Person.objects.get(id_parladata=int(out[2]['id'])), votes2=out[2]['ratio'], person3=Person.objects.get(id_parladata=int(out[3]['id'])), votes3=out[3]['ratio'], person4=Person.objects.get(id_parladata=int(out[4]['id'])), votes4=out[4]['ratio'], person5=Person.objects.get(id_parladata=int(out[5]['id'])), votes5=out[5]['ratio'])
    return HttpResponse('All iz well')

def getLessEqualVoters(request, person_id, date=None):
	equalVoters = getPersonCardModel(LessEqualVoters, person_id)
	out = {
        'person': {
            'name': Person.objects.get(id_parladata=int(person_id)).name,
            'id': int(person_id)
        },
        'results': [
            {
                "ratio": equalVoters.votes1,
                "id": equalVoters.person1.id_parladata,
                "name": equalVoters.person1.name,
                "party": requests.get(API_URL+'/getMPParty/' + str(equalVoters.person1.id_parladata)).json(),
            },
            {
                "ratio": equalVoters.votes2,
                "id": equalVoters.person2.id_parladata,
                "name": equalVoters.person2.name,
                "party": requests.get(API_URL+'/getMPParty/' + str(equalVoters.person2.id_parladata) + '/').json(),
            },
            {
                "ratio": equalVoters.votes3,
                "id": equalVoters.person3.id_parladata,
                "name": equalVoters.person3.name,
                "party": requests.get(API_URL+'/getMPParty/' + str(equalVoters.person3.id_parladata) + '/').json(),
            },
            {
                "ratio": equalVoters.votes4,
                "id": equalVoters.person4.id_parladata,
                "name": equalVoters.person4.name,
                "party": requests.get(API_URL+'/getMPParty/' + str(equalVoters.person4.id_parladata) + '/').json(),
            },
            {
                "ratio": equalVoters.votes5,
                "id": equalVoters.person5.id_parladata,
                "name": equalVoters.person5.name,
                "party": requests.get(API_URL+'/getMPParty/' + str(equalVoters.person5.id_parladata) + '/').json(),
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
	#	members[key].update({'ratio':out[key]})
	outs = sorted(members, key=lambda k: k['ratio'])

	#outs = {key:members[key] for key in keys[-5:]}
	return JsonResponse(outs[-5:], safe=False)


def setCutVotes(request, person_id):

	#Add data of person to dictionary
	"""
		ObjectOut: output dictionary
		rootKey: root key
		id: id of person
		objectIn: dictionary with persons
	"""
	def getIdImageName(ObjectOut, rootKey, ids, objectIn):
		ObjectOut[rootKey+"ID"] = []
		ObjectOut[rootKey+"Name"] = []
		ObjectOut[rootKey+"Image"] = []
		for id in ids:
			ObjectOut[rootKey+"ID"].append(str(id))
			ObjectOut[rootKey+"Name"].append(objectIn[str(id)]['name'])
			ObjectOut[rootKey+"Image"].append(objectIn[str(id)]['image'])

	r=requests.get(API_URL+'/getVotes/')
	votes = r.json()

	r=requests.get(API_URL+'/getMembersOfPGs/')
	membersInPGs = r.json()

	r=requests.get(API_URL+'/getCoalitionPGs/')
	coalition = r.json()

	memList = getMPsList(request)
	members = {str(mp['id']):mp for mp in json.loads(memList.content)}

	votes_count = len(Vote.objects.all())

	out = dict()
	out["for"] = dict()
	out["against"] = dict()
	out["abstain"] = dict()

	#Calculations for this member
	out["for"]["this"]=normalize(sum(map(voteFor, votes[person_id].values())),votes_count)
	out["against"]["this"]=normalize(sum(map(voteAgainst, votes[person_id].values())),votes_count)
	out["abstain"]["this"]=normalize(sum(map(voteAbstain, votes[person_id].values())),votes_count)
	memReq = getMPStaticPL(request, person_id)
	memberData = json.loads(memReq.content)
	out["thisName"]=memberData['person']['name']

	#Calculations for coalition
	idsForCoal, coalFor = zip(*[(member,sum(map(voteFor,votes[str(member)].values()))) for i in coalition['coalition'] for member in membersInPGs[str(i)]])
	idsCoalAgainst, coalAgainst = zip(*[(member,sum(map(voteAgainst,votes[str(member)].values()))) for i in coalition['coalition'] for member in membersInPGs[str(i)]])
	idsCoalAbstain, coalAbstain = zip(*[(member,sum(map(voteAbstain,votes[str(member)].values()))) for i in coalition['coalition'] for member in membersInPGs[str(i)]])

	coalMaxPercentFor = max(coalFor)
	coalMaxPercentAgainst = max(coalAgainst)
	coalMaxPercentAbstain = max(coalAbstain)

	out["for"]["coalition"]=normalize(sum(coalFor)/len(coalFor),votes_count)
	out["for"]["maxCoal"]=normalize(coalMaxPercentFor,votes_count)
	idsMaxForCoal = numpy.array(idsForCoal)[numpy.where(numpy.array(coalFor) == coalMaxPercentFor)[0]]
	getIdImageName(out["for"], "maxCoal", idsMaxForCoal, members)

	out["against"]["coalition"]=normalize(sum(coalAgainst)/len(coalAgainst),votes_count)
	out["against"]["maxCoal"]=normalize(coalMaxPercentAgainst,votes_count)
	idsMaxAgainstCoal = numpy.array(idsCoalAgainst)[numpy.where(numpy.array(coalAgainst) == coalMaxPercentAgainst)[0]]
	getIdImageName(out["against"], "maxCoal", idsMaxAgainstCoal, members)

	out["abstain"]["coalition"]=normalize(sum(coalAbstain)/len(coalAbstain),votes_count)
	out["abstain"]["maxCoal"]=normalize(coalMaxPercentAbstain,votes_count)
	idsMaxAbstainCoal = numpy.array(idsCoalAbstain)[numpy.where(numpy.array(coalAbstain) == coalMaxPercentAbstain)[0]]
	getIdImageName(out["abstain"], "maxCoal", idsMaxAbstainCoal, members)

	#Calculations for opozition
	#delete coalition groups from members in PGs
	map(membersInPGs.__delitem__, [str(coalitionIds) for coalitionIds in coalition['coalition']])
	idsForOpp, oppFor = zip(*[(member,sum(map(voteFor,votes[str(member)].values()))) for i in membersInPGs.keys() for member in membersInPGs[str(i)]])
	idsOppAgainst ,oppAgainst = zip(*[(member,sum(map(voteAgainst,votes[str(member)].values()))) for i in membersInPGs.keys() for member in membersInPGs[str(i)]])
	idsOppAbstain, oppAbstain = zip(*[(member,sum(map(voteAbstain,votes[str(member)].values()))) for i in membersInPGs.keys() for member in membersInPGs[str(i)]])
	oppMaxPercentFor = max(oppFor)
	oppMaxPercentAgainst = max(oppAgainst)
	oppMaxPercentAbstain = max(oppAbstain)

	out["for"]["opozition"]=normalize(sum(oppFor)/len(oppFor),votes_count)
	out["for"]["maxOpp"]=normalize(oppMaxPercentFor,votes_count)

	memReq = getMPStaticPL(request, idsForOpp[oppFor.index(oppMaxPercentFor)])
	memberData = json.loads(memReq.content)
	idsMaxForOppo = numpy.array(idsForOpp)[numpy.where(numpy.array(oppFor) == oppMaxPercentFor)[0]]
	getIdImageName(out["for"], "maxOpp", idsMaxForOppo, members)

	out["against"]["opozition"]=normalize(sum(oppAgainst)/len(oppAgainst),votes_count)
	out["against"]["maxOpp"]=normalize(oppMaxPercentAgainst,votes_count)
	memReq = getMPStaticPL(request, idsOppAgainst[oppAgainst.index(oppMaxPercentAgainst)])
	memberData = json.loads(memReq.content)
	idsMaxAgainstOppo = numpy.array(idsOppAgainst)[numpy.where(numpy.array(oppAgainst) == oppMaxPercentAgainst)[0]]
	getIdImageName(out["against"], "maxOpp", idsMaxAgainstOppo, members)

	out["abstain"]["opozition"]=normalize(sum(oppAbstain)/len(oppAbstain),votes_count)
	out["abstain"]["maxOpp"]=normalize(oppMaxPercentAbstain,votes_count)

	memReq = getMPStaticPL(request, idsOppAbstain[oppAbstain.index(oppMaxPercentAbstain)])
	memberData = json.loads(memReq.content)
	idsMaxAbstainOppo = numpy.array(idsOppAbstain)[numpy.where(numpy.array(oppAbstain) == oppMaxPercentAbstain)[0]]
	getIdImageName(out["abstain"], "maxOpp", idsMaxAbstainOppo, members)

	final_response = saveOrAbort(
        CutVotes,
        person = Person.objects.get(id_parladata=person_id),
        this_for = out["for"]["this"],
        this_against = out["against"]["this"],
        this_abstain = out["abstain"]["this"],
        coalition_for = out["for"]["coalition"],
        coalition_against = out["against"]["coalition"],
        coalition_abstain = out["abstain"]["coalition"],
        coalition_for_max = out["for"]["maxCoal"],
        coalition_against_max = out["against"]["maxCoal"],
        coalition_abstain_max = out["abstain"]["maxCoal"],
        coalition_for_max_person = ','.join(map(str, out["for"]["maxCoalID"])),
        coalition_against_max_person = ','.join(map(str, out["against"]["maxCoalID"])),
        coalition_abstain_max_person = ','.join(map(str, out["abstain"]["maxCoalID"])),
        opposition_for = out["for"]["opozition"],
        opposition_against = out["against"]["opozition"],
        opposition_abstain = out["abstain"]["opozition"],
        opposition_for_max =out["for"]["maxOpp"],
        opposition_against_max = out["against"]["maxOpp"],
        opposition_abstain_max = out["abstain"]["maxOpp"],
        opposition_for_max_person = ','.join(map(str, out["for"]["maxOppID"])),
        opposition_against_max_person = ','.join(map(str, out["against"]["maxOppID"])),
        opposition_abstain_max_person = ','.join(map(str, out["abstain"]["maxOppID"]))
    )

	return JsonResponse(out)


def getCutVotes(request, person_id, date=None):
	cutVotes = getPersonCardModel(CutVotes, person_id, date)

	out = {
        'person': {
            'id': int(person_id),
            'name': Person.objects.get(id_parladata=int(person_id)).name
        },
        'results': {
            'abstain': {
                'score': cutVotes.this_abstain,
                'maxCoalition': {
                    'mps': [{'name': person.name, 'id': person.id_parladata} for person in Person.objects.filter(id_parladata__in=[int(textid) for textid in cutVotes.coalition_abstain_max_person.split(',')])],
                    'score': cutVotes.coalition_abstain_max
                },
                'maxOpposition': {
                    'mps': [{'name': person.name, 'id': person.id_parladata} for person in Person.objects.filter(id_parladata__in=[int(textid) for textid in cutVotes.opposition_abstain_max_person.split(',')])],
                    'score': cutVotes.opposition_abstain_max
                },
                "avgOpposition": {'score': cutVotes.opposition_abstain},
                "avgCoalition": {'score': cutVotes.coalition_abstain},
            },
            "against": {
                'score': cutVotes.this_against,
                'maxCoalition': {
                    'mps': [{'name': person.name, 'id': person.id_parladata} for person in Person.objects.filter(id_parladata__in=[int(textid) for textid in cutVotes.coalition_against_max_person.split(',')])],
                    'score': cutVotes.coalition_against_max
                },
                'maxOpposition': {
                    'mps': [{'name': person.name, 'id': person.id_parladata} for person in Person.objects.filter(id_parladata__in=[int(textid) for textid in cutVotes.opposition_against_max_person.split(',')])],
                    'score': cutVotes.opposition_against_max
                },
                "avgOpposition": {'score': cutVotes.opposition_against},
                "avgCoalition": {'score': cutVotes.coalition_against},
            },
            'for': {
                'score': cutVotes.this_for,
                'maxCoalition': {
                    'mps': [{'name': person.name, 'id': person.id_parladata} for person in Person.objects.filter(id_parladata__in=[int(textid) for textid in cutVotes.coalition_for_max_person.split(',')])],
                    'score': cutVotes.coalition_for_max
                },
                'maxOpposition': {
                    'mps': [{'name': person.name, 'id': person.id_parladata} for person in Person.objects.filter(id_parladata__in=[int(textid) for textid in cutVotes.opposition_for_max_person.split(',')])],
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
#	for i in content.keys():
#		data[i] = [len(speech.split()) for speech in content[i]]
#
#	for i in data.keys():
#		allMPs[i] = sum(data[i])
#
#	thisMP = allMPs[id]
#	average = sum(allMPs.values()) / 90
#	maximumMP = max(allMPs.iterkeys(), key=(lambda key: allMPs[key]))
#	maximum = allMPs[maximumMP]
#
#	toDB = SpokenWords(person = Person.objects.get(id_parladata=id),
#					maxMP = Person.objects.get(id_parladata=maximumMP),
#					average = average,
#					maximum = maximum
#					)
#	#toDB.save()
#
#	return JsonResponse(allMPs)

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
        'results': {
            'privzdignjeno': card.privzdignjeno,
            'problematicno': card.problematicno,
            'preprosto': card.preprosto,
            'average': {
                'privzdignjeno_average': card.privzdignjeno_average,
                'problematicno_average': card.problematicno_average,
                'preprosto_average': card.preprosto_average
            }
        },
        'person': {
            'id': int(person_id),
            'name': Person.objects.get(id_parladata=int(person_id)).name
        }
    }

    return JsonResponse(out, safe=False)

def getTotalStyleScores(request):
    speeches = requests.get(API_URL+'/getAllSpeeches/').json()
    speeches_content = [speech['content'] for speech in speeches]
    speeches_megastring = string.join(speeches_content)

    counter = Counter()
    counter = countWords(speeches_megastring, counter)
    total = sum(counter.values())
    output = {'problematicno': getScore(problematicno, counter, total),
              'privzdignjeno': getScore(privzdignjeno, counter, total),
              'preprosto': getScore(preprosto, counter, total),
#              'total': total
             }

    return JsonResponse(output, safe=False)

def makeAverageStyleScores():
    speeches = requests.get(API_URL+'/getAllSpeeches/').json()
    speeches_content = [speech['content'] for speech in speeches]
    speeches_megastring = string.join(speeches_content)

    counter = Counter()
    counter = countWords(speeches_megastring, counter)
    total = sum(counter.values())
    output = {'problematicno': getScore(problematicno, counter, total),
              'privzdignjeno': getScore(privzdignjeno, counter, total),
              'preprosto': getScore(preprosto, counter, total),
             }

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
        'person': {
            'name': Person.objects.get(id_parladata=int(person_id)).name,
            'id': int(person_id)
        },
        'results': card.data
    }

    return JsonResponse(out)

def setVocabularySize(request, person_id):

    thisperson = Person.objects.get(id_parladata=int(person_id))

    mps = requests.get(API_URL+'/getMPs/').json()

    vocabulary_sizes = []
    result = {}

    for mp in mps:

        speeches = requests.get(API_URL+'/getSpeeches/' + str(mp['id'])).json()

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

    if saveOrAbort(VocabularySize, person=thisperson, score=result['person'], maxMP=maxMP, average=result['average'], maximum=result['max']):
        return HttpResponse('All iz well')
    else:
        return HttpResponse('All was well')

    result_ = saveOrAbort(model=VocabularySize, person=Person.objects.get(id_parladata=int(person_id)), this_person=result[0]['vocabulary_size'], maxMP=Person.objects.get(id_parladata=int(vocabularies_sorted[-1]['person_id'])), average=float(sum(scores))/float(len(scores)), maximum=vocabularies_sorted[-1]['vocabulary_size'])

    return JsonResponse(result, safe=False)

def getVocabularySize(request, person_id, date=None):

    card = getPersonCardModel(VocabularySize, person_id, date)

    out = {
        'person': {
            'name': Person.objects.get(id_parladata=int(person_id)).name,
            'id': int(person_id)
        },
        'results': {
            'max': {
                'score': card.maximum,
                'id': card.maxMP.id_parladata
            },
            'average': card.average,
            'score': card.score
        }
    }

    return JsonResponse(out, safe=False)

def setAverageNumberOfSpeechesPerSession(request, person_id):

    mps = requests.get(API_URL+'/getMPs/').json()

    numbers_of_speeches = []
    result = []

    number_of_sessions = len(requests.get(API_URL+'/getSessions/').json())

    for mp in mps:

        mp_speeches = requests.get(API_URL+'/getSpeeches/' + str(mp['id'])).json()

        if str(mp['id']) == person_id:
            result.append({'person_id': mp['id'], 'avg_speeches_per_session': len(mp_speeches)/number_of_sessions})

        numbers_of_speeches.append({'person_id': mp['id'], 'avg_speeches_per_session': float(len(mp_speeches))/float(number_of_sessions)})

    numbers_sorted = sorted(numbers_of_speeches, key=lambda k: k['avg_speeches_per_session'])

    result.append({'person_id': numbers_sorted[-1]['person_id'], 'avg_speeches_per_session': numbers_sorted[-1]['person_id']})

    scores = [person['avg_speeches_per_session'] for person in numbers_sorted]

    result.append({'person_id': 'average', 'avg_speeches_per_session': float(sum(scores))/float(len(scores))})

    result_ = saveOrAbort(model=NumberOfSpeechesPerSession, person=Person.objects.get(id_parladata=int(person_id)), person_value=result[0]['avg_speeches_per_session'], maxMP=Person.objects.get(id_parladata=int(result[1]['person_id'])), average=result[2]['avg_speeches_per_session'], maximum=result[1]['avg_speeches_per_session'])

    return JsonResponse(result, safe=False)

def setAverageNumberOfSpeechesPerSession(request, person_id):

    person = Person.objects.get(id_parladata=int(person_id))
    speeches = requests.get(API_URL+'/getSpeechesOfMP/' + person_id).json()
    no_of_speeches = len(speeches)

    no_of_sessions = 12 # TODO

    score = no_of_speeches/no_of_sessions

    mps = requests.get(API_URL+'/getMPs/').json()
    mp_scores = []

    for mp in mps:
        mp_no_of_speeches = len(requests.get(API_URL+'/getSpeechesOfMP/' + str(mp['id'])).json())

        mp_no_of_sessions = 12 # TODO

        mp_scores.append({'id': mp['id'], 'score': mp_no_of_speeches/mp_no_of_sessions})


    mp_scores_sorted = sorted(mp_scores, key=lambda k: k['score'])

    average = sum([mp['score'] for mp in mp_scores])/len(mp_scores)

    saveOrAbort(model=AverageNumberOfSpeechesPerSession, person=person, score=score, average=average, maximum=mp_scores_sorted[-1]['score'], maxMP=Person.objects.get(id_parladata=int(mp['id'])))

    return HttpResponse('All iz well')

def getAverageNumberOfSpeechesPerSession(request, person_id, date=None):

    card = getPersonCardModel(AverageNumberOfSpeechesPerSession, person_id, date)

    out = {
        'person': {
            'name': Person.objects.get(id_parladata=int(person_id)).name,
            'id': int(person_id)
        },
        'results': {
            'max': {
                'score': card.maximum,
                'id': card.maxMP.id_parladata
            },
            'average': card.average,
            'score': card.score
        }
    }

    return JsonResponse(out, safe=False)