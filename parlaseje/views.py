# -*- coding: UTF-8 -*-
from datetime import datetime

from parlalize.utils import *
import requests
import json
from django.http import JsonResponse
from parlaseje.models import *
from parlalize.settings import API_URL


# Create your views here.

def setAllSessions(request):
    data  = requests.get(API_URL+'/getSessions/').json()
    for sessions in data:
        if not Session.objects.filter(id_parladata=sessions['id']):
            result = Session(name=sessions['name'],
                             gov_id=sessions['gov_id'],
                             start_time=sessions['start_time'],
                             end_time=sessions['end_time'],
                             classification=sessions['classification'],
                             id_parladata=sessions['id'])
            result.save()

    return JsonResponse({'alliswell': True})

#def getDZSessions(request):
#
#    return JsonResponse(out, safe=False)

def setMotionOfSession(request, id_se):
    votes = vote_parladata.objects.filter(motion__session__id = id_se)
    data = {}

    data = {vote.motion.id:{'text':vote.motion.text,
                       'result':vote.motion.result,
                       'yes':Ballot.objects.filter(vote = vote, option = 'za').count(),
                       'no':Ballot.objects.filter(vote = vote, option = 'proti').count(),
                       'notOn':Ballot.objects.filter(vote = vote, option = 'ni').count(),
                       'kvorum':Ballot.objects.filter(vote = vote, option = 'kvorum').count()}   for vote in votes}




    return JsonResponse({'alliswell': True})

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
