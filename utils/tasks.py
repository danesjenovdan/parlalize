# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from time import sleep
from raven.contrib.django.raven_compat.models import client
from itertools import groupby

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.test.client import RequestFactory
from django.core.exceptions import PermissionDenied

from parlalize.utils_ import getAllStaticData, tryHard
from parlaposlanci.views import (setMPStaticPL, setMembershipsOfMember, setLastActivity,
                                 setAverageNumberOfSpeechesPerSessionAll, setVocabularySizeAndSpokenWords,
                                 setCompass, setListOfMembersTickers, setPresenceThroughTime,
                                 setMinsterStatic, setPercentOFAttendedSession, setNumberOfQuestionsAll)
from parlaskupine.views import setMPsOfPG, setBasicInfOfPG, setWorkingBodies, setVocabularySizeALL, getListOfPGs, setPresenceThroughTime as setPresenceThroughTimePG, setPGMismatch, setNumberOfQuestionsAll as setNumberOfQuestionsAllPG
from parlalize.settings import API_URL, SETTER_KEY, DASHBOARD_URL, SETTER_KEY

from utils.votes_pg import set_mismatch_of_pg

from utils.votes import setAllVotesCards
from utils.recache import recacheCards
from utils.imports import updateOrganizations


import requests
import json
import inspect

status_api = DASHBOARD_URL + '/api/status/'

factory = RequestFactory()
request_with_key = factory.get('?key=' + SETTER_KEY)

setters = {
    # parlaposlanci
    'setMPStaticPL': {'setter': setMPStaticPL, 'group': 'parlaposlanci', 'type': 'single'},
    'setMembershipsOfMember': {'setter': setMembershipsOfMember, 'group': 'parlaposlanci', 'type': 'single'},
    'setAverageNumberOfSpeechesPerSessionAll': {'setter': setAverageNumberOfSpeechesPerSessionAll, 'group': 'parlaposlanci', 'type': 'all'},
    'setVocabularySizeAndSpokenWords': {'setter': setVocabularySizeAndSpokenWords, 'group': 'parlaposlanci', 'type': 'all'},
    'setCompass': {'setter': setCompass, 'group': 'parlaposlanci', 'type': 'single'},
    'setListOfMembersTickers': {'setter': setListOfMembersTickers, 'group': 'parlaposlanci', 'type': 'all'},
    'setPresenceThroughTime': {'setter': setPresenceThroughTime, 'group': 'parlaposlanci', 'type': 'single'},
    'setMinsterStatic': {'setter': setMinsterStatic, 'group': 'parlaposlanci', 'type': 'single'},
    'setPercentOFAttendedSession': {'setter': setPercentOFAttendedSession, 'group': 'parlaposlanci', 'type': 'single'},
    'setNumberOfQuestionsAll': {'setter': setNumberOfQuestionsAll, 'group': 'parlaposlanci', 'type': 'all'},
    'set_mismatch_of_pg': {'setter': set_mismatch_of_pg, 'group': 'parlaposlanci', 'type': 'all'},
    'setAllVotesCards': {'setter': setAllVotesCards, 'group': 'parlaposlanci', 'type': 'all'},

    # parlaskupine
    'setMPsOfPG': {'setter': setMPsOfPG, 'group': 'parlaskupine', 'type': 'single'}, 
    'setBasicInfOfPG': {'setter': setBasicInfOfPG, 'group': 'parlaskupine', 'type': 'single'},
    'setWorkingBodies': {'setter': setWorkingBodies, 'group': 'parlaskupine', 'type': 'single'},
    'setVocabularySizeALL': {'setter': setVocabularySizeALL, 'group': 'parlaskupine', 'type': 'all'},
    'setPresenceThroughTimePG': {'setter': setPresenceThroughTimePG, 'group': 'parlaskupine', 'type': 'single'},
    'setPGMismatch': {'setter': setPGMismatch, 'group': 'parlaskupine', 'type': 'single'},
    'setNumberOfQuestionsAllPG': {'setter': setNumberOfQuestionsAllPG, 'group': 'parlaskupine', 'type': 'all'},

    # recache
    'setAllStaticData': {'setter': getAllStaticData, 'group': 'recache'},

    # utils
    'updateOrganizations': {'setter': updateOrganizations, 'group': 'utils', 'type': 'all'},
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
def runAsyncSetter(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print data
        status_id = data.pop('status_id')
        auth_key = request.META['HTTP_AUTHORIZATION']
        if auth_key != SETTER_KEY:
            print("auth fail")
            sendStatus(status_id, "Fail", "Authorization fails", ['buuu'])
            raise PermissionDenied
        print("auth OK")
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

        runCardsSetters.apply_async((methods, status_id), queue='parlalize')
            
    else:
        return JsonResponse({'status': 'this isnt post'})

    return JsonResponse({'status':'runned'})


@shared_task
def recache_cards(data, status_id):
    sendStatus(status_id, "Running", "It looks ok", ['Running recaching'])
    args = {'pgCards':[],
            'mpCards':[],
            'sessions':{},
            'votes_of_s':[],
            'sender': sendStatus,
            'status_id': status_id}

    if data['location'] == 'p':
        args['mpCards'] = data['setters']
    if data['location'] == 'ps':
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
def runCardsSetters(methods, status_id):
    print 'running'
    methots_objs = {method: setters[method] for method in methods}
    data = {'parlaposlanci': {},
            'parlaskupine': {},
            'utils': {}}

    # group setters by location and type
    for key, group in groupby(methots_objs.items(), lambda x: x[1]['group']):
        for k, g in groupby(group, lambda x: x[1]['type']):
            data[key][k] = [i for i in g]

    if data['parlaposlanci']:
        memberships = tryHard(API_URL + '/getMPs/').json()
        oIDs = [member['id'] for member in memberships]
        app = 'parlaposlanci'

    elif data['parlaskupine']:
        membersOfPGsRanges = tryHard(
            'https://data.parlameter.si/v1/getMembersOfPGsRanges/').json()
        oIDs = [key for key, value in membersOfPGsRanges[-1]['members'].items() if len(value) > 1]
        app = 'parlaskupine'
    elif data['utils']:
        app = 'utils'


    # run setters for each member
    done = []
    i=1
    if 'single' in data[app].keys():
        data_len = float(len(oIDs))
        try:
            print oIDs
            for m in oIDs:
                print m
                current = []
                print data[app]['single']
                for setter in data[app]['single']:
                    func = setter[1]['setter']
                    done.append({str(m): func(request_with_key, str(m)).content})
                    current.append(setter[0])
                #done.append({m: current})
                sendStatus(status_id, "Running" , str(int(i/data_len*100)) + "%", done)
                i += 1
        except:
            print "except"
            sendStatus(status_id, "Fails", "Look at the sentry log", done)
            client.captureException()

    # run all in one setters (one call for all members)
    if 'all' in data[app].keys():
        for i, setter in enumerate(data[app]['all']):
            print setter
            sendStatus(status_id, "Start" , str(int(float(i+1)/len(data[app]['all'])*100)) + "%", done)
            func = setter[1]['setter']
            sendStatus(status_id, "Running" , str(int(float(i+1)/len(data[app]['all'])*100)) + "%", done)
            if len(inspect.getargspec(func).args):
                done.append(func(request_with_key).content)
            else:
                done.append(func())
            #done.append(setter[0])
    print done
    sendStatus(status_id, "Done", "It looks ok", done)


@shared_task
def runPartysSetters():
    pass


def sendStatus(status_id, type_, note, data):
    requests.put(status_api + str(status_id)+'/',
                 data= {
                            "status_type": type_,
                            "status_note": note,
                            "status_done": str(data)
                        })
