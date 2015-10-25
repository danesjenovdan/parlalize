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
    data  = requests.get(API_URL+'/getSessions/').json()
    for sessions in data:
        result = saveOrAbort(model=Session,
                             name=sessions['name'],
                            gov_id=sessions['gov_id'],
                            start_time=sessions['start_time'],
                            end_time=sessions['end_time'],
                            classification=sessions['classification'],
                            id_parladata=sessions['id']
                            )

    return JsonResponse({'alliswell': True})

#def getDZSessions(request):
#
#    return JsonResponse(out, safe=False)

    #Session
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
    motion  = requests.get('http://data.parlameter.si/v1/motionOfSession/'+str(id_se)+'/').json()
    votes  = requests.get('http://data.parlameter.si/v1/getVotesOfSession/'+str(id_se)+'/').json()
    #napisi se za un graf: za:{kolk:40,poslanci:[32,4,3,4],pg{ZL:23,SDS:23}}
    
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


        result = saveOrAbort(model=Vote,
                            session=Session.objects.get(id_parladata=int(id_se)),
                            motion=mot['text'],
                            votes_for=yes,
                            against=no,
                            abstain=kvorum,
                            not_present=not_present,
                            result=mot['result'],
                            id_parladata=mot['id']
                            )


        vg = saveOrAbort(model=Vote_graph,
                            motion=mot['text'],
                            votes_for=yes,
                            against=no,
                            abstain=kvorum,
                            not_present=not_present,
                            result=mot['result'],
                            id_parladata=mot['id'],
                            pgs_yes=yesdic,
                            pgs_no=nodic,
                            pgs_np=npdic,
                            pgs_kvor=kvordic,
                            mp_yes = tabyes,
                            mp_no = tabno,
                            mp_np = tabnp,
                            mp_kvor = tabkvo
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

    out = {
        'results': {

                'motion_id': card.id_parladata,
                'text': card.motion,
                'votes for': card.votes_for,
                'againt': card.against,
                'abstain': card.abstain,
                'not_present':card.not_present,
                'result':card.result,
                'pgs_yes':card.pgs_yes,
                'pgs_no':card.pgs_no,
                'pgs_kvor':card.pgs_kvor,
                'pgs_np':card.pgs_np
        }
    }


    return JsonResponse(out, safe=False)