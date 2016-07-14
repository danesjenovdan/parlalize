# -*- coding: UTF-8 -*-
from datetime import datetime

from parlalize.utils import *
import requests
import json
from django.http import JsonResponse
from parlaseje.models import *
from parlalize.settings import API_URL, API_DATE_FORMAT
from parlaseje.utils import *
from collections import defaultdict
from math import fabs
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

def getSpeech(request, speech_id):
    speech = Speech.objects.get(id_parladata=speech_id)
    out={"speech_id":speech.id_parladata, "content":speech.content}
    result = {
        'person': {
            'name': speech.person.name,
            'id': int(speech.person.id_parladata)
        },
        'results': out
    }
    return JsonResponse(result)

def getSessionSpeeches(request, session_id):
    out = []
    session = Session.objects.get(id_parladata=session_id)
    for speech in Speech.objects.filter(session=session).order_by("-start_time"):
        out.append({"speech_id": speech.id_parladata, "content": speech.content, "person_id": speech.person.id_parladata})
    result = {
        'session': {
            'name': session.name,
            'id': int(session.id_parladata)
        },
        'results': out
    }
    return JsonResponse(result, safe=False)

def setMotionOfSession(request, id_se):
    motion  = requests.get(API_URL + '/motionOfSession/'+str(id_se)+'/').json()
    session = Session.objects.get(id_parladata=id_se)
    tab = []
    yes = 0
    no = 0
    kvorum = 0
    not_present = 0
    option = ""
    tabyes = []
    tabno = []
    tabkvo = []
    tabnp = []
    yesdic = defaultdict(int)
    nodic = defaultdict(int)
    kvordic = defaultdict(int)
    npdic = defaultdict(int)
    tyes = []
    for mot in motion:
        votes  = requests.get(API_URL + '/getVotesOfMotion/'+str(mot['vote_id'])+'/').json()
        for vote in votes:
            if vote['option'] == str('za'):
                yes = yes + 1
                yesdic[vote['pg_id']] += 1
                #TODO da ti seteje po acronymu
                tabyes.append(vote['mp_id'])
            if vote['option'] == str('proti'):
                no = no + 1
                nodic[vote['pg_id']] += 1
                tabno.append(vote['mp_id'])

            if vote['option'] == str('kvorum'):
                kvorum = kvorum + 1
                kvordic[vote['pg_id']] += 1
                tabkvo.append(vote['mp_id'])
            if vote['option'] == str('ni'):
                not_present = not_present + 1
                npdic[vote['pg_id']] += 1
                tabnp.append(vote['mp_id'])
        result = saveOrAbortNew(model=Vote,
                                   created_for=session.start_time,
                                   session=Session.objects.get(id_parladata=int(id_se)),
                                   motion=mot['text'],
                                   votes_for=yes,
                                   against=no,
                                   abstain=kvorum,
                                   not_present=not_present,
                                   result=mot['result'],
                                   id_parladata=mot['vote_id'],
                                   id_parladata_session=int(id_se)
                                   )

        vg = saveOrAbort(model=Vote_graph,
                         motion=mot['text'],
                         votes_for=yes,
                         against=no,
                         abstain=kvorum,
                         not_present=not_present,
                         result=mot['result'],
                         id_parladata=mot['vote_id'],
                         pgs_yes=yesdic,
                         pgs_no=nodic,
                         pgs_np=npdic,
                         pgs_kvor=kvordic,
                         mp_yes=tabyes,
                         mp_no=tabno,
                         mp_np=tabnp,
                         mp_kvor=tabkvo
                         )
        yes = 0
        no = 0
        kvorum = 0
        not_present = 0
        tabyes = []
        tabno = []
        tabkvo = []
        tabnp = []
        yesdic = defaultdict(int)
        nodic = defaultdict(int)
        kvordic = defaultdict(int)
        npdic = defaultdict(int)
    return JsonResponse({'alliswell': True})


def getMotionOfSession(request, id_se, date=False):
    out = []
    if Vote.objects.filter(session__id_parladata=id_se):
        if date:
            model = Vote.objects.filter(session__id_parladata=id_se, start_time__lte=datetime.strptime(date, '%d.%m.%Y'))
        else:
            model = Vote.objects.filter(session__id_parladata=id_se)

        for card in model:
            out.append({
            'session': {

                'name': Session.objects.get(id_parladata=int(id_se)).name,
                'date': Session.objects.get(id_parladata=int(id_se)).start_time.date(),
                'id': int(id_se)
            },
            'results': {

                    'motion_id': card.id_parladata,
                    'text': card.motion,
                    'votes_for': card.votes_for,
                    'against': card.against,
                    'abstain': card.abstain,
                    'not_present':card.not_present,
                    'result':card.result
            }
        })
    else:
        return JsonResponse({"status": "No card MOFO"}, safe=False)
    return JsonResponse(out, safe=False)


def getMotionGraph(request, id_se):
    card = getGraphCardModel(Vote_graph, id_se)


    option_for = {
        'option': 'za',
        'total_votes': card.votes_for,
        'breakdown': []
    }
    option_against = {
        'option': 'proti',
        'total_votes': card.against,
        'breakdown': []
    }
    option_kvor = {
        'option': 'kvorum',
        'total_votes': card.abstain,
        'breakdown': []
    }
    option_np = {
        'option': 'ni',
        'total_votes': card.not_present,
        'breakdown': []
    }

    parties = requests.get(API_URL + '/getAllPGsExt/').json()
    mps = requests.get(API_URL + '/getMPs/').json()

    for i, party in enumerate(card.pgs_yes):
        option_for['breakdown'].append({
            'acronym': parties[party]['acronym'],
            'party_id': int(party),
            'total_votes': card.pgs_yes[party],
            'mps': []
        })

        for person_id in card.mp_yes:
            mp = filter(lambda person: person['id'] == int(person_id), mps)
            if len(mp) > 0:
                mp = mp[0]
                if mp['party_id'] == int(party):
                    option_for['breakdown'][i]['mps'].append({
                        'name': mp['name'],
                        'id': person_id,
                        'gov_id': mp['gov_id'],
                        'party': {
                            'acronym': parties[party]['acronym'],
                            'id': int(party),
                            'name': parties[party]['name']
                        }
                    })

    for i, party in enumerate(card.pgs_no):
        option_against['breakdown'].append({
            'acronym': parties[party]['acronym'],
            'party_id': int(party),
            'total_votes': card.pgs_no[party],
            'mps': []
        })

        for person_id in card.mp_no:
            mp = filter(lambda person: person['id'] == int(person_id), mps)
            if len(mp) > 0:
                mp = mp[0]
                if mp['party_id'] == int(party):
                    option_against['breakdown'][i]['mps'].append({
                        'name': mp['name'],
                        'id': person_id,
                        'gov_id': mp['gov_id'],
                        'party': {
                            'acronym': parties[party]['acronym'],
                            'id': int(party),
                            'name': parties[party]['name']
                        }
                    })

    for i, party in enumerate(card.pgs_kvor):
        option_kvor['breakdown'].append({
            'acronym': parties[party]['acronym'],
            'party_id': int(party),
            'total_votes': card.pgs_kvor[party],
            'mps': []
        })

        for person_id in card.mp_kvor:
            mp = filter(lambda person: person['id'] == int(person_id), mps)
            if len(mp) > 0:
                mp = mp[0]
                if mp['party_id'] == int(party):
                    option_kvor['breakdown'][i]['mps'].append({
                        'name': mp['name'],
                        'id': person_id,
                        'gov_id': mp['gov_id'],
                        'party': {
                            'acronym': parties[party]['acronym'],
                            'id': int(party),
                            'name': parties[party]['name']
                        }
                    })

    for i, party in enumerate(card.pgs_np):
        option_np['breakdown'].append({
            'acronym': parties[party]['acronym'],
            'party_id': int(party),
            'total_votes': card.pgs_np[party],
            'mps': []
        })

        for person_id in card.mp_np:
            mp = filter(lambda person: person['id'] == int(person_id), mps)
            if len(mp) > 0:
                mp = mp[0]
                if mp['party_id'] == int(party):
                    option_np['breakdown'][i]['mps'].append({
                        'name': mp['name'],
                        'id': person_id,
                        'gov_id': mp['gov_id'],
                        'party': {
                            'acronym': parties[party]['acronym'],
                            'id': int(party),
                            'name': parties[party]['name']
                        }
                    })

    out = {
        'results': {

                'motion_id': card.id_parladata,
                'text': card.motion,
                'votes_for': card.votes_for,
                'against': card.against,
                'abstain': card.abstain,
                'not_present':card.not_present,
                'result':card.result,
                'pgs_yes':card.pgs_yes,
                'pgs_no':card.pgs_no,
                'pgs_kvor':card.pgs_kvor,
                'pgs_np':card.pgs_np,
                'mp_yes':card.mp_yes,
                'mp_no':card.mp_no,
                'mp_kvor':card.mp_kvor,
                'mp_np':card.mp_np,
                'layered_data': [option_for, option_against, option_kvor, option_np]
        }
    }


    return JsonResponse(out, safe=False)

def setAbsentMPs(request, id_se):
    votes = requests.get(API_URL + '/getVotesOfSession/'+str(id_se)+'/').json()
    session = Session.objects.get(id_parladata=id_se)
    mps = requests.get(API_URL+'/getMPs/'+ session.start_time.strftime(API_DATE_FORMAT)).json()

  
    mpsID = []

    if len(votes) != 0:
        mpsID = [mpID['id'] for mpID in mps]
        for vote in votes:
            if vote['option'] != 'ni':
                if vote['mp_id'] in mpsID:
                    mpsID.remove(vote['mp_id'])
  

        result = saveOrAbortNew(model=AbsentMPs,
                                id_parladata=id_se,
                                absentMPs=mpsID,
                                created_for=session.start_time
                                )
   
        mpsID = []
    return JsonResponse({'alliswell': True})
    

def getAbsentMPs(request, id_se, date=False):
    try:
        if date:
            ids = AbsentMPs.objects.get(id_parladata=int(id_se), start_time__lte=datetime.strptime(date, '%d.%m.%Y')).absentMPs
        else:
            ids = AbsentMPs.objects.get(id_parladata=int(id_se)).absentMPs

        mps = requests.get(API_URL+'/getMPs/').json()
        
        results = []
        
        for abMP in ids:
            for mp in mps:
                if str(mp['id']) == str(abMP):
                    results.append({"id":mp['id'], "gov_id":mp['gov_id'],'name':mp['name'], 'acronym':mp['acronym'], 'image':mp['image']})
                    
    except ObjectDoesNotExist:
        return JsonResponse({"status": "No card MOFO"}, safe=False)
    return JsonResponse(results, safe=False)

def setPresenceOfPG(request, id_se):
    votes = requests.get(API_URL+'/getVotesOfSession/'+str(id_se)+'/').json()
    motions = requests.get(API_URL+'/motionOfSession/'+str(id_se)+'/').json()
    session = Session.objects.get(id_parladata=id_se)
    membersOfPG = requests.get(API_URL+'/getMembersOfPGsOnDate/'+ session.start_time.strftime(API_DATE_FORMAT)).json()

    onSession = {}
    yesdic = defaultdict(int)
    allsessionsinone = defaultdict(list)
    final = {}
    numOfMPs = {}
    results = {}
    allPgs = {}

    if len(votes) != 0:
        for vote in votes:
            if vote['option'] != 'ni':
                if vote['mo_id'] in onSession.keys():
                    onSession[vote['mo_id']].append(vote['pg_id'])
                else:
                    onSession.update({vote['mo_id'] : [vote['pg_id']]})
    
    for i in membersOfPG:
        allPgs[i] = len(membersOfPG[i]) * len(motions)
        
    for b in onSession:
        for i in onSession[b]:
            yesdic[i] += 1
        results[b] = yesdic
    
    if len(results)>0:
        temp = dict(results[results.keys()[0]])
        for i in temp:
            if allPgs[str(i)] != 0:
                final[i] = int((float(temp[i]) / float(allPgs[str(i)])) * 100)

        result = saveOrAbortNew(model=PresenceOfPG,
                                created_for=session.start_time,
                                presence=[final],
                                id_parladata = int(id_se)
                                )

    return JsonResponse({'alliswell': True})

def getPresenceOfPG(request, id_se, date=False):

    results = []
    try:
        if date:
            presence = PresenceOfPG.objects.get(id_parladata=id_se, start_time__lte=datetime.strptime(date, '%d.%m.%Y'))
        else:
            presence = PresenceOfPG.objects.get(id_parladata=id_se)
        
            for p in presence.presence[0]:
                results.append({"id":Organization.objects.get(id_parladata=p).id_parladata, "name":Organization.objects.get(id_parladata=p).name, "percent":presence.presence[0][p], "acronym":Organization.objects.get(id_parladata=p).acronym})
    except ObjectDoesNotExist:
        return JsonResponse({"status": "No card MOFO"}, safe=False)
    return JsonResponse(results, safe=False)

def setSpeechesOnSession(request, date=False):
    if date:
        numberOfSessions = len(Session.objects.filter(start_time__lte=datetime.strptime(date, '%d.%m.%Y')))
        mps = requests.get(API_URL+'/getMPs/'+ date).json()
    else:
        numberOfSessions = len(Session.objects.filter(start_time__lte=datetime.now().date()).json())
        mps = requests.get(API_URL+'/getMPs/'+  str(datetime.now().date().strftime(API_DATE_FORMAT))).json()
        date = datetime.now().date()

    mpsID = {}
    for mp in mps: 
        speech = len(requests.get(API_URL+'/getSpeechesOfMP/'+ str(mp['id'])+'/'+ date).json())
        if numberOfSessions !=0:
            mpsID.update({mp['id']:float(float(speech)/float(numberOfSessions))})
    date = datetime.strptime(date, '%d.%m.%Y')
    result = saveOrAbortNew(model=AverageSpeeches,
                                created_for=date,
                                speechesOnSession=mpsID
                                )
    return JsonResponse({'alliswell': True})


def getMinSpeechesOnSession(request, date=False):
    results = []
    try:
        if date:
            averageSpeeches = AverageSpeeches.objects.get(created_for=datetime.strptime(date, '%d.%m.%Y')).speechesOnSession
            mps = requests.get(API_URL+'/getMPs/'+ date).json()
        else:
            averageSpeeches = AverageSpeeches.objects.get().speechesOnSession
            mps = requests.get(API_URL+'/getMPs/'+  str(datetime.now().date().strftime(API_DATE_FORMAT))).json()
    


        sort = sorted(averageSpeeches.items(), key=lambda x:x[1])
        
        for s in sort:
            for mp in mps:
                if int(s[0]) == int(mp['id']):
                    results.append({"id":mp['id'], "gov_id":mp['gov_id'], "name": mp['name'], "image":mp['image'], "speeches":s[1]})
    except ObjectDoesNotExist:
        return JsonResponse({"status": "No card MOFO"}, safe=False)
    return JsonResponse(results, safe=False)


def getMaxSpeechesOnSession(request, date=False):
    results = []
    try:
        if date:
            averageSpeeches = AverageSpeeches.objects.get(created_for = datetime.strptime(date, '%d.%m.%Y')).speechesOnSession
            mps = requests.get(API_URL+'/getMPs/'+ date).json()
        else:
            averageSpeeches = AverageSpeeches.objects.get().speechesOnSession
            mps = requests.get(API_URL+'/getMPs/'+ str(datetime.now().date().strftime(API_DATE_FORMAT))).json()
    


        sort = sorted(averageSpeeches.items(), key=lambda x:x[1], reverse=True)
        for s in sort:
            for mp in mps:
                if int(s[0]) == int(mp['id']):
                    results.append({"id":mp['id'], "gov_id":mp['gov_id'], "name": mp['name'], "image":mp['image'], "speeches":s[1]})
        
    except ObjectDoesNotExist:
        return JsonResponse({"status": "No card MOFO"}, safe=False)
    return JsonResponse(results, safe=False)



def runSetters(request, date_to):
   
    
    setters_models = {
        #Vote: setMotionOfSession,
        PresenceOfPG: setPresenceOfPG,
        AbsentMPs: setAbsentMPs,
        AverageSpeeches: setSpeechesOnSession   
    }
    for model, setter in setters_models.items():
        dates = findDatesFromLastCard(model, None, date_to)
        print dates
        if dates==[]:
            continue
        if model != AverageSpeeches:
            IDs = getSesIDs(dates[1],dates[-1])
            for ID in IDs:
                setter(request, str(ID))        
        else:
            datesSes = getSesDates(dates[-1])
            for date in datesSes:
                setter(request, date.strftime(API_DATE_FORMAT))
    return JsonResponse({"status": "all is fine :D"}, safe=False)
