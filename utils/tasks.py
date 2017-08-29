# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from time import sleep
from raven.contrib.django.raven_compat.models import client

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.test.client import RequestFactory

from parlalize.utils_ import getAllStaticData, tryHard
from parlaposlanci.views import setMPStaticPL, setMembershipsOfMember, setLastActivity, setAverageNumberOfSpeechesPerSessionAll, setVocabularySizeAndSpokenWords, setCompass, setListOfMembersTickers, setPresenceThroughTime, setMinsterStatic
from parlaskupine.views import setMPsOfPG, setBasicInfOfPG, setWorkingBodies, setVocabularySizeALL, getListOfPGs, setPresenceThroughTime as setPresenceThroughTimePG, setPGMismatch
from parlalize.settings import API_URL, SETTER_KEY

from utils.recache import recacheCards

import requests
import json

factory = RequestFactory()
request_with_key = factory.get('?key=' + SETTER_KEY)

setters = {
    # parlaposlanci
    'setMPStaticPL': {'setter': setMPStaticPL, 'group': 'parlaposlanci'},
    'setMembershipsOfMember': {'setter': setMembershipsOfMember, 'group': 'parlaposlanci'},
    'setAverageNumberOfSpeechesPerSessionAll': {'setter': setAverageNumberOfSpeechesPerSessionAll, 'group': 'parlaposlanci'},
    'setVocabularySizeAndSpokenWords': {'setter': setVocabularySizeAndSpokenWords, 'group': 'parlaposlanci'},
    'setCompass': {'setter': setCompass, 'group': 'parlaposlanci'},
    'setListOfMembersTickers': {'setter': setListOfMembersTickers, 'group': 'parlaposlanci'},
    'setPresenceThroughTime': {'setter': setPresenceThroughTime, 'group': 'parlaposlanci'},
    'setMinsterStatic': {'setter': setMinsterStatic, 'group': 'parlaposlanci'},

    # parlaskupine
    'setMPsOfPG': {'setter': setMPsOfPG, 'group': 'parlaskupine'}, 
    'setBasicInfOfPG': {'setter': setBasicInfOfPG, 'group': 'parlaskupine'},
    'setWorkingBodies': {'setter': setWorkingBodies, 'group': 'parlaskupine'},
    'setVocabularySizeALL': {'setter': setVocabularySizeALL, 'group': 'parlaskupine'},
    'getListOfPGs': {'setter': getListOfPGs, 'group': 'parlaskupine'},
    'setPresenceThroughTimePG': {'setter': setPresenceThroughTimePG, 'group': 'parlaskupine'},
    'setPGMismatch': {'setter': setPGMismatch, 'group': 'parlaskupine'},

    # utils
    'setAllStaticData': {'setter': getAllStaticData, 'group': 'recache'}, 
}
#members cards
recache = {
    'osnovne-informacije'
    'zadnje-aktivnosti'
    'prisotnost-skozi-cas'
    'izracunana-prisotnost-seje'
    'izracunana-prisotnost-glasovanja'
    'poslanska-vprasanja-in-pobude'
    'st-poslanskih-vprasanj-in-pobud'
    'clanstva'
    'glasovanja'
    'najveckrat-enako'
    'najmanjkrat-enako'
    'tfidf'
    'povezave-do-govorov'
    'stevilo-izgovorjenih-besed'
    'povprecno-stevilo-govorov-na-sejo'
    'besedni-zaklad'
    'stilne-analize'

    'kompas'
}

@csrf_exempt
def runAsyncRecacheCards(request):
    print('ivan')
    if request.method == 'POST':
        data = json.loads(request.body)
        print data
        status_id = data.pop('status_id')

        



@csrf_exempt
def runAsyncSetter(request):
    print('ivan')
    if request.method == 'POST':
        data = json.loads(request.body)
        print data
        status_id = data.pop('status_id')

        if data['type'] == 'recache':
            print 'recache'
            recache.apply_async((data['setters'], status_id), queue='parlalize')
            return JsonResponse({'status':'runned'})
        elif data['type'] == 'recache_cards':
            recache_cards.apply_async((data, status_id), queue='parlalize')
            return JsonResponse({'status':'runned'})
            print 'recache cards'
        print 'group setter'
        methods = data['setters']

        runMembersSetters.apply_async((methods, status_id), queue='parlalize')
            
    else:
        return JsonResponse({'status': 'this isnt post'})

    return JsonResponse({'status':'runned'})


@shared_task
def recache_cards(data, status_id):
    args = {'pgCards':[],
            'mpCards':[],
            'sessions':{},
            'votes_of_s':[],
            'sender': sendStatus,
            'status_id': status_id}

    if data['location'] == 'p':
        args['mpCards'] = data['setters']
    if data['location'] == 'pg':
        args['pgCards'] = data['setters']
    recacheCards(**args)

@shared_task
def recache(caches, status_id):
    print 'reache'
    merhods = [setters[cache]['setter'] for cache in caches]
    caches = setters[cache]['setter']
    sendStatus(status_id, "Running", "It looks ok", ['Running recaching'])
    for cache in merhods:
        cache(None, force_render=True)
    sendStatus(status_id, "Done", "It looks ok", ['CACHED'])


@shared_task
def runMembersSetters(methods, status_id):
    print 'members'
    methods = [(setter, setters[setter]['setter']) for setter in methods]
    memberships = tryHard(API_URL + '/getMPs/').json()
    mIDs = [member['id'] for member in memberships]

    done = []
    i=1
    try:
        print mIDs
        for m in mIDs:
            print m
            current = []
            print methods
            for setter in methods:
                func = setter[1]
                print func(request_with_key, str(m)).content
                current.append(setter[0])
            done.append({m: current})
            sendStatus(status_id, "Running" , str(int(i/90.*100)) + "%", done)
            i += 1
    except:
        print "except"
        sendStatus(status_id, "Fails", "Look at the sentry log", done)
        client.captureException()
    sendStatus(status_id, "Done", "It looks ok", done)


@shared_task
def runPartysSetters():
    pass


def sendStatus(status_id, type_, note, data):
    requests.put('http://localhost:8888/api/status/'+str(status_id)+'/',
                 data= {
                            "status_type": type_,
                            "status_note": note,
                            "status_done": data
                        })