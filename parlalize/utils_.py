# -*- coding: UTF-8 -*-
from datetime import datetime, timedelta
from django.http import Http404, JsonResponse, HttpResponse
import requests
from parlaposlanci.models import (Person, StyleScores, CutVotes, MPStaticPL,
                                  MembershipsOfMember, LessEqualVoters,
                                  EqualVoters, Presence,
                                  AverageNumberOfSpeechesPerSession,
                                  VocabularySize, Compass, SpokenWords,
                                  LastActivity, MinisterStatic)
from parlaskupine.models import (Organization, WorkingBodies,
                                 CutVotes as CutVotesPG,
                                 DeviationInOrganization, LessMatchingThem,
                                 MostMatchingThem, PercentOFAttendedSession,
                                 MPOfPg, PGStatic,
                                 VocabularySize as VocabularySizePG,
                                 StyleScores as StyleScoresPG)
from parlaseje.models import (VoteDetailed, Session, Vote, Ballot, Speech, Tag,
                              PresenceOfPG, AbsentMPs, VoteDetailed, Quote, Question)
from parlalize.settings import (VOTE_MAP, API_URL, BASE_URL, API_DATE_FORMAT,
                                DEBUG, API_OUT_DATE_FORMAT, GLEJ_URL, ALL_STATIC_CACHE_AGE, slack_token)
from django.contrib.contenttypes.models import ContentType
import requests
import json
import time
import csv
import itertools
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from parlalize.settings import SETTER_KEY, VOTE_NAMES
from requests.auth import HTTPBasicAuth

from slackclient import SlackClient

def lockSetter(function):
    def wrap(request, *args, **kwargs):
        if request:
            setterKey = request.GET.get('key')
            if str(setterKey) == str(SETTER_KEY):
                return function(request, *args, **kwargs)
            else:
                raise PermissionDenied
        else:
            return function(*args, **kwargs)
    return wrap


def tryHard(url):
    data = None
    counter = 0
    while data is None:
        try:
            if counter > 2:
                client.captureMessage(url+' je zahinavu več ko 2x.')
                return
            data = requests.get(url)
        except:
            counter += 1
            time.sleep(5)
            pass
        counter += 1
    return data


def normalize(val, max_):
    try:
        return round((float(val)*100)/float(max_))
    except:
        return val


# checks if cards with the data exists or not
# DEPRICATED
def saveOrAbort(model, **kwargs):
    savedModel = model.objects.filter(**kwargs)
    if savedModel:
        # Add cards which has always uninqe data
        if model != LastActivity:
            lastModel = model.objects.latest('created_at')
            if savedModel.latest('created_at').id != lastModel.id:
                newModel = model(**kwargs)
                newModel.save()
                return True
        else:
            return False
    else:
        newModel = model(**kwargs)
        newModel.save()
        return True
    return False


def saveOrAbortNew(model, **kwargs):
    # checks if cards with the data exists or not NEW
    """
    usage:
        watch parlaposlanci/views.py:setMembershipsOfMember

        if you use saveOrAbortNew in setter you need to use
        getPersonCardModelNew in getter
    """
    def save_it(model, created_for, **kwargs):
        kwargs.update({'created_for': created_for})
        newModel = model(**kwargs)
        newModel.save()
        return True
    if model != LastActivity:
        created_for = kwargs.pop('created_for')
    # print kwargs
    savedModel = model.objects.filter(**kwargs)

    if savedModel:
        if 'person' in kwargs:
            if model != LastActivity:
                person_id = kwargs['person'].id_parladata
                cards = model.objects.filter(person__id_parladata=person_id,
                                             created_for__lte=created_for)
                if cards:
                    lastDate = cards.latest('created_for').created_for
                else:
                    lastDate = datetime.min

                if savedModel.latest('created_for').created_for != lastDate:
                    save_it(model, created_for, **kwargs)

        elif 'organization' in kwargs:
            party_id = kwargs['organization'].id_parladata
            models = model.objects.filter(organization__id_parladata=party_id,
                                          created_for__lte=created_for)
            if models:
                # if allready exist write in DB for thiw PG
                lastDate = models.latest('created_for').created_for
                if savedModel.latest('created_for').created_for != lastDate:
                    save_it(model, created_for, **kwargs)
            else:
                save_it(model, created_for, **kwargs)

        elif 'session' in kwargs:
            ses_id = kwargs['session'].id_parladata
            models = model.objects.filter(session__id_parladata=ses_id)
            lastDate = models.latest('created_at').created_for
            if savedModel.latest('created_for').created_for != lastDate:
                save_it(model, created_for, **kwargs)
    else:
        if model != LastActivity:
            kwargs.update({'created_for': created_for})
        newModel = model(**kwargs)
        newModel.save()
        return True
    return False


def findDatesFromLastCard(model, id, lastParsedDate, minDate=None):
    toDate = datetime.strptime(lastParsedDate, '%d.%m.%Y').date()

    print model._meta.app_label
    try:
        if model._meta.app_label == 'parlaposlanci':
            models = model.objects.filter(person__id_parladata=id)
            lastCardDate = models.order_by('-created_for')[0].created_for
        elif model._meta.app_label == 'parlaskupine':
            models = model.objects.filter(organization__id_parladata=id)
            lastCardDate = models.order_by('-created_for')[0].created_for
        elif model._meta.app_label == 'parlaseje':
            models = model.objects.all()
            lastCardDate = models.order_by('-created_for')[0].created_for
    except:
        lastCardDate = datetime.strptime('02.08.2014', '%d.%m.%Y').date()
    # lastCardDate = lastCardDate.replace(tzinfo=None)
    if minDate:
        od = datetime.strptime(minDate, '%d.%m.%Y').date()
        lastCardDate = datetime.strptime(minDate, '%d.%m.%Y').date()
        if od > lastCardDate:
            lastCardDate = od

    return [(lastCardDate+timedelta(days=days))
            for days
            in range((toDate-lastCardDate).days)]


def datesGenerator(stDate, toDate):
    dates = [(stDate + timedelta(days=x))
             for x
             in range(0, (toDate - stDate).days)]
    return dates


def getPersonCardModelNew(model, id, date=None, is_visible=None):
    if date:
        dateObj = datetime.strptime(date, '%d.%m.%Y')
        modelObject = model.objects.filter(person__id_parladata=id,
                                           created_for__lte=dateObj)
    else:
        modelObject = model.objects.filter(person__id_parladata=id,
                                           created_for__lte=datetime.now())
    if is_visible:
        modelObject = modelObject.filter(is_visible=True)

    if not modelObject:
        # if model == LastActivity:
            # return None
        if DEBUG:
            raise Http404('Nismo našli kartice' + str(model)+str(id))
        else:
            raise Http404('Nismo našli kartice')
    else:
        if model == LastActivity:
            latest_day = modelObject.latest('created_for').created_for
            print latest_day
            if len(modelObject.filter(created_for=latest_day)) > 1:
                models = modelObject.filter(created_for=latest_day)
                modelObject = models.latest('created_at')
            else:
                modelObject = modelObject.latest('created_for')
        else:
            date = modelObject.latest('created_for').created_for
            models = modelObject.filter(created_for=date)
            modelObject = models.latest('created_at')
            # modelObject = modelObject.latest('created_for')
    return modelObject


# DEPRICATED
def getPersonCardModel(model, id, date=None):
    if date:
        dateObj = datetime.strptime(date, '%d.%m.%Y')
        if model == LastActivity:
            modelObject = model.objects.filter(person__id_parladata=id,
                                               date__lte=dateObj)
        else:
            dateObj
            modelObject = model.objects.filter(person__id_parladata=id,
                                               created_at__lte=dateObj)
    else:
        if model == LastActivity:
            modelObject = model.objects.filter(person__id_parladata=id,
                                               date__lte=datetime.now())
        else:
            modelObject = model.objects.filter(person__id_parladata=id,
                                               created_at__lte=datetime.now())
    if not modelObject:
        if model == LastActivity:
            return None
        raise Http404('Nismo našli kartice')
    else:
        if model == LastActivity:
            modelObject = modelObject.latest('date')
        else:
            modelObject = modelObject.latest('created_at')
    return modelObject


def getPGCardModel(model, id, date=None):
    if date:
        dateObj = datetime.strptime(date, '%d.%m.%Y')
        modelObject = model.objects.filter(organization__id_parladata=id,
                                           created_at__lte=dateObj)
    else:
        modelObject = model.objects.filter(organization__id_parladata=id,
                                           created_at__lte=datetime.now())
    if not modelObject:
        raise Http404('Nismo našli kartice')
    else:
        modelObject = modelObject.latest('created_at')
    return modelObject


def getPGCardModelNew(model, id, date=None, is_visible=None):
    if date:
        dateObj = datetime.strptime(date, '%d.%m.%Y')
        modelObject = model.objects.filter(organization__id_parladata=id,
                                           created_for__lte=dateObj)
    else:
        modelObject = model.objects.filter(organization__id_parladata=id,
                                           created_for__lte=datetime.now())

    if is_visible:
        modelObject = modelObject.filter(is_visible=True)

    if not modelObject:
        # if model == LastActivity:
            # return None
        raise Http404('Nismo našli kartice')
    else:
        date = modelObject.latest('created_for').created_for
        modelObject = modelObject.filter(created_for=date).latest('created_at')
    return modelObject


def getSCardModel(model, id_se, date=None):
    if date:
        dateObj = datetime.strptime(date, '%d.%m.%Y')
        modelObject = model.objects.filter(id_parladata=id_se,
                                           created_at__lte=dateObj)
    else:
        modelObject = model.objects.filter(id_parladata=id_se,
                                           created_at__lte=datetime.now())
    if not modelObject:
        raise Http404('Nismo našli kartice')
    else:
        modelObject = modelObject.latest('created_at')
    return modelObject


# get all PG ID's
def getPGIDs():
    data = tryHard(API_URL+'/getAllPGsExt/').json()

    return [pg for pg in data]


def getMPGovId(id_parladata):
    person = Person.objects.filter(id_parladata=id_parladata)[0]
    out = {'id': person.id_parladata,
           'gov_id': person.gov_id}
    return out


def getPersonData(id_parladata, date_=None):
    if not date_:
        date_ = datetime.now().strftime(API_DATE_FORMAT)
    try:
        data = getPersonCardModelNew(MPStaticPL, id_parladata, date_)
    except:
        url = API_URL + '/getPersonData/' + str(id_parladata) + '/'
        guest = tryHard(url).json()
        gov_id = None
        if guest and guest['gov_id']:
            return {
                'type': 'visitor' if guest else 'unknown',
                'party': {'acronym': None,
                          'id': None,
                          'name': None,
                          'is_coalition': None},
                'name': guest['name'] if guest else None,
                'gov_id': guest['gov_id'],
                'id': id_parladata,
                'district': None,
                'gender': None,
                'is_active': None,
                'has_function': False,
                }
        else:
            return {'type': 'visitor' if guest else 'unknown',
                    'party': {'acronym': None,
                              'id': None,
                              'name': None,
                              'is_coalition': None},
                    'name': guest['name'] if guest else None,
                    'gov_id': None,
                    'id': id_parladata,
                    'district': None,
                    'gender': None,
                    'is_active': None,
                    'has_function': False,
                    }
    try:
        partyData = data.party.getOrganizationData()
    except:
        print 'Nima org', data.person.name
        partyData = {'acronym': None,
                     'id': None,
                     'name': None,
                     'is_coalition': None}
    return {
            'type': 'mp',
            'name': data.person.name,
            'id': int(data.person.id_parladata),
            'gov_id': data.gov_id,
            'party': partyData,
            'gender': data.gender,
            'district': data.district,
            'is_active': True if data.person.actived == 'True' else False,
            'has_function': data.person.has_function,
        }


def getMinistryData(id_parladata, date_=None):
    if not date_:
        date_ = datetime.now().strftime(API_DATE_FORMAT)
    try:
        data = getPersonCardModelNew(MinisterStatic, id_parladata, date_)
        return {
                'type': "ministry",
                'name': data.person.name,
                'id': int(data.person.id_parladata),
                'gov_id': data.gov_id,
                'party': data.party.getOrganizationData() if data.party else None,
                'ministry': data.ministry.getOrganizationData() if data.ministry else None,
                'gender': data.gender,
                'district': data.district,
                'is_active': True if data.person.actived == "True" else False,
                'has_function': data.person.has_function,
            }
    except:
        return getPersonData(id_parladata, date_)


def getPersonDataAPI(request, id_parladata, date_=None):
    data = getPersonData(id_parladata, date_)
    return JsonResponse(data)


def modelsData(request):
    out = []
    for ct in ContentType.objects.all():
        m = ct.model_class()

        out.append({'model': m.__module__,
                    'Ime modela': m.__name__,
                    'st:': m._default_manager.count()})
    return JsonResponse(out, safe=False)


def getAllStaticData(request, force_render=False):
    sc = SlackClient(slack_token)
    date_of = datetime.now().date()
    date_ = date_of.strftime(API_DATE_FORMAT)

    c_data = cache.get('all_statics')
    if c_data and not force_render:
        out = c_data
    else:
        sc.api_call("chat.postMessage",
                    channel="#parlalize_notif",
                    text='StaticDataDebug start: ' + str(c_data)[:100] + ' ' + str(force_render))

        date_ = datetime.now().strftime(API_DATE_FORMAT)

        out = {'persons': {}, 'partys': {}, 'wbs': {}, 'sessions': {}, 'ministrs': {}}
        for person in Person.objects.all():
            personData = getPersonData(person.id_parladata,
                                       date_)
            out['persons'][person.id_parladata] = personData
        parliamentary_group = Organization.objects.filter(classification__in=settings.PS_NP)
        for party in parliamentary_group:
            out['partys'][party.id_parladata] = party.getOrganizationData()

        sessions = Session.objects.all()
        for session in sessions:
            out['sessions'][session.id_parladata] = session.getSessionData()

        ministrs = MinisterStatic.objects.all()
        for ministr in ministrs:
            out['ministrs'][ministr.id] = ministr.getJsonData() 

        working_bodies = ['odbor', 'komisija', 'preiskovalna komisija']
        orgs = Organization.objects.filter(classification__in=working_bodies)
        out['wbs'] = [{'id': org.id_parladata,
                       'name': org.name} for org in orgs]

        cache.set('all_statics', out, 60 * 60 * ALL_STATIC_CACHE_AGE)
        sc.api_call("chat.postMessage",
                    channel="#parlalize_notif",
                    text='StaticDataDebug end: ' + str(out)[:100] + ' ' + str(force_render))

    return JsonResponse(out)


def getPersonsCardDates(request, person_id):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = ('attachment; filename="'
                                       '' + str(person_id) + ''
                                       '.csv"')

    mems = tryHard(API_URL + '/getAllTimeMemberships').json()
    member_dates = [mem for mem in mems if str(mem['id']) == person_id]

    dates = {}
    dates['is_member'] = []
    for d in member_dates:
        if d['start_time']:
            start = datetime.strptime(d['start_time'].split('T')[0],
                                      '%Y-%m-%d')
        else:
            start = datetime(day=1, month=8, year=2014)
        if d['end_time']:
            end = datetime.strptime(d['end_time'].split('T')[0],
                                    '%Y-%m-%d')
        else:
            end = datetime.today()
        while end > start:
            dates['is_member'].append(start.strftime(API_DATE_FORMAT))
            start = start+timedelta(days=1)

    models = {'spoken': SpokenWords,
              'presence': Presence,
              'style': StyleScores,
              'equal': EqualVoters,
              'less_equal': LessEqualVoters,
              'static': MPStaticPL,
              'number_of_speeches': AverageNumberOfSpeechesPerSession,
              'memberships': MembershipsOfMember,
              'last_activity': LastActivity,
              'vocabolary_size': VocabularySize,
              }

    for key, model in models:
        modelz = model.objects.filter(person__id_parladata=person_id)
        datez = modelz.order_by('created_for').values_list('created_for',
                                                           flat=True)
        dates[key] = [day.strftime(API_DATE_FORMAT) for day in datez]

    writer = csv.writer(response)
    keys = dates.keys()
    writer.writerow(['Date']+keys)
    date = datetime(day=1, month=8, year=2014)
    while date < datetime.today():
        print date
        strDate = date.strftime(API_DATE_FORMAT)
        writer.writerow([strDate]+['Yes' if strDate in dates[key] else ''
                                   for key in keys])
        date = date + timedelta(days=1)

    return response


def getOrgsCardDates(request, org_id):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = ('attachment; filename="'
                                       '' + str(org_id) + ''
                                       '.csv"')

    dates = {}

    models = {'PGStatic': PGStatic,
              'PercentOFAttendedSession': PercentOFAttendedSession,
              'MPOfPg': MPOfPg,
              'MostMatchingThem': MostMatchingThem,
              'LessMatchingThem': LessMatchingThem,
              'DeviationInOrganization': DeviationInOrganization,
              'vocabulary_size': VocabularySizePG,
              'style_scores': StyleScoresPG,
              }
    for key, model in models:
        modelz = model.objects.filter(organization__id_parladata=org_id)
        datez = modelz.order_by('created_for').values_list('created_for',
                                                           flat=True)
        dates[key] = [day.strftime(API_DATE_FORMAT) for day in datez]

    datez = static.order_by('created_for').values_list('created_for',
                                                       flat=True)

    writer = csv.writer(response)
    keys = dates.keys()
    writer.writerow(['Date']+keys)
    date = datetime(day=1, month=8, year=2014)
    while date < datetime.today():
        print date
        strDate = date.strftime(API_DATE_FORMAT)
        writer.writerow([strDate]+['Yes' if strDate in dates[key] else ''
                                   for key in keys])
        date = date + timedelta(days=1)

    return response


def monitorMe(request):

    r = requests.get(BASE_URL + '/p/getMPStatic/2/')
    if r.status_code == 200:
        return HttpResponse('All iz well.')
    else:
        return HttpResponse('PANIC!')


def printProgressBar(iteration,
                     total,
                     prefix='',
                     suffix='',
                     decimals=1,
                     length=100,
                     fill='█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r' + prefix + '|' + bar + '|' + percent + suffix + '\r')
    # Print New Line on Complete
    if iteration == total:
        print()


def setQuoteSourceSpeeachToLatestValid(session_id):
    quotes = Quote.objects.filter(speech__session__id_parladata=session_id)
    for quote in quotes:
        print quote.id
        speech = quote.speech
        lastSpeech = Speech.getValidSpeeches(datetime.now()).filter(person=speech.person,
                                                                    order=speech.order,
                                                                    session__id_parladata=session_id,
                                                                    start_time=speech.start_time)
        if lastSpeech:
            print speech.content[0:100], speech.person, speech.order, speech.start_time, speech.id_parladata
            print (lastSpeech[0].content[0:100], lastSpeech[0].id_parladata)
            print lastSpeech.count()
            quote.speech = lastSpeech[0]
            quote.save()
        else:
            print "fejl"
            print speech.content[0:100], speech.person, speech.order, speech.start_time, speech.id_parladata
            lastSpeech = Speech.getValidSpeeches(datetime.now()).filter(person=speech.person,
                                                                        order=speech.order-20,
                                                                        session__id_parladata=session_id,
                                                                        start_time=speech.start_time)
            if lastSpeech:
                print "Juhej debug"
                print speech.content[0:100], speech.person, speech.order, speech.start_time, speech.id_parladata
                print (lastSpeech[0].content[0:100], lastSpeech[0].id_parladata)
                print lastSpeech.count()
                quote.speech = lastSpeech[0]
                quote.save()


def prepareTaggedBallots(datetime_obj, ballots, card_owner_data):
    """
    generic method which return tagged ballots for partys and members
    """
    votes = Vote.objects.filter(start_time__lte=datetime_obj).order_by('start_time')
    votes = votes.filter(id__in=ballots.keys())
    # add start_time_date to querySetObjets
    votes = votes.extra(select={'start_time_date': 'DATE(start_time)'})
    # get unique dates
    dates = list(set(list(votes.values_list("start_time_date", flat=True))))
    dates.sort()
    data = {date: [] for date in dates}
    #current_data = {'date': votes[0].start_time_date, 'ballots': []}
    for vote in votes:
        try:
            temp_data = {
                'motion': vote.motion,
                'vote_id': vote.id_parladata,
                'result': vote.result,
                'classification': vote.classification,
                'session_id': vote.session.id_parladata if vote.session else None,
                'option': ballots[vote.id][1],
                'tags': vote.tags,
            }
            # if party
            if 'party' in  card_owner_data.keys():
                temp_data['party'] = card_owner_data['party']['id']
                disunions = vote.vote_intradisunion.filter(organization__id_parladata=card_owner_data['party']['id'])
                if len(disunions) > 0:
                    temp_data['disunion'] = disunions[0].maximum
            if ballots[vote.id][0]:
                temp_data['ballot_id'] = ballots[vote.id][0]
            data[vote.start_time_date].append(temp_data)
        except:
            print 'Ni vota ' + str(vote.id)

    out = [{'date': date.strftime(API_OUT_DATE_FORMAT),
            'ballots': data[date]}
           for date in dates]

    tags = list(Tag.objects.all().values_list('name', flat=True))
    result = {
        'created_at': dates[-1].strftime(API_DATE_FORMAT) if dates else None,
        'created_for': dates[-1].strftime(API_DATE_FORMAT) if dates else None,
        'all_tags': tags,
        "classifications": VOTE_NAMES,
        'results': list(reversed(out))
        }
    result.update(card_owner_data)
    return result


@lockSetter
def recacheLastSession(request):
    requests.get(GLEJ_URL + '/c/zadnja-seja/?frame=true&altHeader=true&state=%7B%7D&forceRender=true')
    requests.get(GLEJ_URL + '/c/zadnja-seja/?embed=true&altHeader=true&state=%7B%7D&forceRender=true')
    requests.get(GLEJ_URL + '/c/zadnja-seja/?forceRender=true')
    requests.get(GLEJ_URL + '/sta/zadnja-seja/?frame=true&altHeader=true&state=%7B%7D&forceRender=true')
    requests.get(GLEJ_URL + '/sta/zadnja-seja/?embed=true&altHeader=true&state=%7B%7D&forceRender=true')
    requests.get(GLEJ_URL + '/sta/zadnja-seja/?forceRender=true')

    return HttpResponse('check it out')


def checkIfQuestionRecipinetsDuplication():
    for q in list(Question.objects.all())[:100]:
        recpt = list(q.recipient_persons_static.all())
        for a, b in itertools.combinations(recpt, 2):
            if a.getJsonData() == b.getJsonData():
                print q.id


def removeMinistrStaticDuplications():
    m_ids = list(set(list(MinisterStatic.objects.all().values_list("person__id_parladata", flat=True))))
    for m in m_ids:
        ms = MinisterStatic.objects.filter(person__id_parladata=m)
        ministrs = list(set(list(ms.values_list("ministry__id_parladata", flat=True))))
        for ministry in ministrs:
            mm = MinisterStatic.objects.filter(person__id_parladata=m,
                                               ministry__id_parladata=ministry)
            for for_del in mm[1:]:
                for_del.delete()


def setCardData(dic, method, pg_id, date_, path, out_keys):
    """
    Mathod is used for get card data. Find data in dictionaty by path and
    set value in a nested dictionary (dic) with given a list (out_keys) of indices
    """
    try:
        card_data = json.loads(method(None, pg_id, date_).content)
        # get data
        for key in path:
            card_data = card_data[key]
    except:
        card_data = None
    # set data
    for key in out_keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[out_keys[-1]] = card_data

import time
def getDataFromPagerApi(url, per_page = None):
    start = time.time()
    data = []
    end = False
    page = 1
    while not end:
        response = requests.get(url + '?page=' + str(page) + ('&per_page='+str(per_page) if per_page else '')).json()
        data += response['data']
        if page >= response['pages']:
            break
        page += 1
    end = time.time()
    print("TIME: ", end - start)
    return data


def getDataFromPagerApiGen(url, per_page = None):
    end = False
    page = 1
    while not end:
        print(page)
        response = requests.get(url + '?page=' + str(page) + ('&per_page='+str(per_page) if per_page else '')).json()
        yield response['data']
        if page >= response['pages']:
            print("brejk")
            break
        page += 1


def getPersonAmendmentsCount(person_id, date_of):
    person = Person.objects.get(id_parladata=person_id)
    card = person.amendments.filter(start_time__lte=date_of)
    count = card.count()
    if not card:
        date = datetime.now()
    else:
        date = card.latest('created_for').created_for
    return person, count, date
