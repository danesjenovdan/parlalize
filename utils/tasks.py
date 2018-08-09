# Create your tasks here
from __future__ import absolute_import, unicode_literals
from django_celery_monitor.models import TaskState
from celery import states, shared_task
from raven.contrib.django.raven_compat.models import client

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.test.client import RequestFactory
from django.core.exceptions import PermissionDenied
from django.forms.models import model_to_dict

from parlalize.utils_ import getAllStaticData, tryHard
from parlalize.settings import API_URL, SETTER_KEY, DASHBOARD_URL, SETTER_KEY

from utils.votes import setAllVotesCards
from utils.recache import recacheCards, recacheListOfSession
from utils import imports

from parlaposlanci import views as members_views
from parlaskupine import views as parties_views
from parlaseje import views as sessions_views
from utils import recache as recache_views

import requests
import json

status_api = DASHBOARD_URL + '/api/status/'

factory = RequestFactory()
request_with_key = factory.get('?key=' + SETTER_KEY)

parlaposlanci_setters = ['setAllVotesCards', 'setNumberOfQuestionsAll',
    'setPercentOFAttendedSession', 'setMinsterStatic', 'setMPStaticPL', 'setMembershipsOfMember',
    'setAverageNumberOfSpeechesPerSessionAll' ,'setVocabularySizeAndSpokenWords', 'setCompass',
    'setListOfMembersTickers', 'setPresenceThroughTime']
parlaskupine_setters = ['setMPsOfPG', 'setBasicInfOfPG',]
parlaseje_setters = ['setMotionOfSession']
import_setters = ['updateOrganizations']

all_in_one = ['setAverageNumberOfSpeechesPerSessionAll', 'setVocabularySizeAndSpokenWords',
    'setListOfMembersTickers', 'setNumberOfQuestionsAll', 'setAllVotesCards', 'updateOrganizations']


@csrf_exempt
def runAsyncSetter(request):
    args = ['method', 'attr']
    if request.method == 'POST':
        data = json.loads(request.body)
        print data
        auth_key = request.META['HTTP_AUTHORIZATION']
        if auth_key != SETTER_KEY:
            print("auth fail")
            raise PermissionDenied

        for setter in data:
            list_args = [setter[element] for element in args if element in setter]
            if setter['type'] == 'recache':
                print 'recache'
                recache.apply_async(list_args, queue='parlalize')
                return JsonResponse({'status':'runned'})
            elif setter['type'] == 'recache_cards':
                recache_cards.apply_async(list_args, queue='parlalize')
                return JsonResponse({'status':'runned'})
                print 'recache cards'
            elif setter['type'] == 'setter':
                print(setter)
                runCardsSetters.apply_async(list_args, queue='parlalize')
            
    else:
        return JsonResponse({'status': 'this isnt post'})

    return JsonResponse({'status':'runned'})


@shared_task
def recache_cards(card, attr):
    args = {'pgCards':[],
            'mpCards':[],
            'sessions':{},
            'votes_of_s':[]}

    if attr == 'p':
        args['mpCards'] = card
    if attr == 'ps':
        args['pgCards'] = card
    recacheCards(**args)


# need some love if is necessary
@shared_task
def recache(caches, attr):
    print 'reache'
    #merhods = [setters[cache]['setter'] for cache in caches]
    #caches = setters[cache]['setter']
    #for cache in merhods:
    #    cache(None, force_render=True)


@shared_task
def runCardsSetters(method_name, attr=None):
    IDs = []
    is_all_in_one = False

    # members
    if method_name in parlaposlanci_setters:
        method = getattr(members_views, method_name)
    elif method_name in parlaskupine_setters:
        method = getattr(parties_views, method_name)
    elif method_name in parlaseje_setters:
        method = getattr(sessions_views, method_name)
    elif method_name in import_setters:
        method = getattr(imports, method_name)
    else:
        return "This method is not registered"
    print(method)
    if not attr:
        if method_name in all_in_one:
            # RUN ALL IN ONE METHOD
            method(request_with_key)
            return 'Done'
        else:
            # Find all active IDs for run on it
            if method_name in parlaposlanci_setters:
                memberships = tryHard(API_URL + '/getMPs/').json()
                IDs = [member['id'] for member in memberships]
            elif method_name in parlaskupine_setters:
                membersOfPGsRanges = tryHard(
                    'https://data.parlameter.si/v1/getMembersOfPGsRanges/').json()
                IDs = [key for key, value in membersOfPGsRanges[-1]['members'].items() if len(value) > 1]
            else:
                return "This setter needs attr"
        
    else:
        IDs.append(attr)
        
    print(IDs)
    for ID in IDs:
        data = [request_with_key, ID]
        print(method(*data))
    return 'Done'


def get_celery_status(request):
    tasks = TaskState.objects.all().order_by('-tstamp')
    objs = [model_to_dict(task) for task in tasks]
    return JsonResponse(objs, safe=False)