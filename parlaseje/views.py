# -*- coding: UTF-8 -*-
from datetime import datetime

from parlalize.utils import *
import requests
import json
from django.http import JsonResponse
from parlaseje.models import *
from parlalize.settings import API_URL
from parlaseje.utils import *
from collections import defaultdict
from math import fabs
# Create your views here.

def setAllSessions(request):
    data  = requests.get(API_URL + '/getSessions/').json()
    for sessions in data:
        if not Session.objects.filter(id_parladata=sessions['id']):

            result = saveOrAbort(model=Session,
                            name=sessions['name'],
                             gov_id=sessions['gov_id'],
                             start_time=sessions['start_time'],
                             end_time=sessions['end_time'],
                             classification=sessions['classification'],
                             id_parladata=sessions['id'])

    return JsonResponse({'alliswell': True})

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

def getSessionSpeeches(request, session_id,):
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
    votes  = requests.get(API_URL + '/getVotesOfSession/'+str(id_se)+'/').json()

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
        for vote in votes:
            if str(vote['mo_id']) == str(mot['id']):
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

        result = saveOrAbortMotion(model=Vote,
                                   session=Session.objects.get(id_parladata=int(id_se)),
                                   motion=mot['text'],
                                   votes_for=yes,
                                   against=no,
                                   abstain=kvorum,
                                   not_present=not_present,
                                   result=mot['result'],
                                   id_parladata=mot['vote_id']
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
    return JsonResponse({'alliswell': True})


def getMotionOfSession(request, id_se):
    out = []
    model  = Vote.objects.filter(session__id_parladata=id_se)
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

    return JsonResponse(out, safe=False)


def getMotionGraph(request, id_se):
    card = getGraphCardModel(Vote_graph, id_se)


    option_for = {
        'option': 'za',
        'total_votes': card.votes_for,
        'breakdown': []
    }
    option_against = {
        'option': 'za',
        'total_votes': card.votes_for,
        'breakdown': []
    }
    option_kvor = {
        'option': 'za',
        'total_votes': card.votes_for,
        'breakdown': []
    }
    option_np = {
        'option': 'za',
        'total_votes': card.votes_for,
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
                'againt': card.against,
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
    mps = requests.get(API_URL+'/getMPs/').json()
    onSession = []
    mpsID = []
    if len(votes) != 0:
        for vote in votes:
            onSession.append(vote['mp_id'])

        onSession = list(set(onSession))
        [mpsID.append(mpID['id'])for mpID in mps]

        for mp in onSession:
            if mp in mpsID:
                mpsID.remove(mp)

        result = saveOrAbortAbsent(model=AbsentMPs,
                                id_parladata=id_se,
                                absentMPs=mpsID
                                )

        return JsonResponse({'alliswell': True})
    else:
        return JsonResponse({'No session with this id':id_se})

def getAbsentMPs(request, id_se):

    mps = requests.get(API_URL+'/getMPs/').json()
    result ={}
    results = {}
    ids = AbsentMPs.objects.get(id_parladata=int(id_se)).absentMPs
    for abMP in ids:
        for mp in mps:
            if str(mp['id']) == str(abMP):
                result = {'name':mp['name'], 'acronym':mp['acronym'], 'image':mp['image']}
                results[mp['id']]= result
    return JsonResponse(results, safe=False)

def setPresenceOfPG(request, id_se):
    membersOfPG = requests.get(API_URL+'/getMembersOfPGs/').json()
    votes = requests.get(API_URL+'/getVotesOfSession/'+str(id_se)+'/').json()
    motions = requests.get(API_URL+'/motionOfSession/'+str(id_se)+'/').json()
    onSession = {}
    yesdic = defaultdict(int)
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

    for b in onSession.keys():
        for i in onSession[b]:
            yesdic[i] += 1
        results[b] = yesdic

    for b in results:
        print results[b]







    '''
    for i in set(onSession):
        for a in membersOfPG:
            if i in membersOfPG[a]:
                yesdic[a] += 1


    for a in yesdic:
        results[a] = float(yesdic[a]) / float(len(motions) *len(membersOfPG[a]))


    '''
    return JsonResponse(results, safe=False)
