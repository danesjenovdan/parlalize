# -*- coding: UTF-8 -*-
from datetime import datetime
from django.http import Http404
from parlaposlanci.models import LastActivity
from parlaseje.models import *
from parlalize.settings import API_URL, API_DATE_FORMAT, LEGISLATION_STATUS, LEGISLATION_RESULT, VOTE_INDICATORS, GLEJ_URL
from django.http import JsonResponse
from parlalize.utils_ import tryHard


def getGraphCardModel(model, id, date=None):
    if date:
        dateObj = datetime.strptime(date, '%d.%m.%Y')
        modelObject = model.objects.filter(id_parladata=id,
                                           created_at__lte=dateObj)
    else:
        modelObject = model.objects.filter(id_parladata=id,
                                           created_at__lte=datetime.now())
    if not modelObject:
        raise Http404('Nismo našli kartice')
    else:
        newModel = model(**kwargs)
        newModel.save()
        return True
    return False


def getSesIDs(start_date, end_date):
    result = []
    data = tryHard(API_URL + '/getSessions/').json()
    session = Session.objects.all()
    for ids in session:
        result.append(ids.id_parladata)
    return result


def getSesDates(end_date):
    result = []
    data = tryHard(API_URL + '/getSessions/').json()
    session = Session.objects.filter(start_time__lte=end_date)
    for ids in session:
        result.append(ids.start_time)
    return result


def getSesCardModelNew(model, id, date=None):
    if date:
        dateObj = datetime.strptime(date, '%d.%m.%Y')
        modelObject = model.objects.filter(session__id_parladata=id,
                                           created_for__lte=dateObj)
    else:
        modelObject = model.objects.filter(session__id_parladata=id,
                                           created_for__lte=datetime.now())

    if not modelObject:
        raise Http404("Nismo našli kartice")
    else:
        modelObject = modelObject.latest('created_for')
        print "get object ", modelObject.created_for
    return modelObject


def resultOfMotion(yes, no, kvorum, not_present, vote_id, date_=None):
    result = tryHard(API_URL + '/getResultOfMotion/' + str(vote_id)).json()
    allMPs = (int(len(tryHard(API_URL + '/getMPs/' +
                              date_.strftime(API_DATE_FORMAT)).json())) * 2) / 3
    if result['result'] == "1" or result['result'] == "1 ":
        return True
    elif result['result'] == "0" or result['result'] == "0 ":
        return False
    else:
        if yes >= allMPs:
            allMPs = 0
            return True
        else:
            allMPs = 0
            return False


def getSessionDataAPI(requests, session_id):
    session = Session.objects.filter(id_parladata=session_id)

    if session:
        return JsonResponse(session[0].getSessionData())
    else:
        return JsonResponse({'name': 'unkonwn',
                             'date': 'unkonwn',
                             'id': 'unkonwn',
                             })


def idsOfSession(model):
    mod = model.objects.all().values_list('session__id_parladata', flat=True)
    ses = tryHard(API_URL + '/getSessions/').json()
    ids = [session['id'] for session in ses]
    if len(mod) == 0:
        return ids
    else:
        return list(set(ids) - set(mod))


def set_status_of_laws():
    legislations = Legislation.objects.all()
    for legislation in legislations:
        votes = Vote.objects.filter(epa=legislation.epa)
        votes = votes.filter(motion__icontains='glasovanje o zakonu v celoti')
        if votes:
            if votes.count() > 1:
                print "FAIL"
                continue
            vote = votes[0]
            legislation.status = LEGISLATION_STATUS[1][0]
            if vote.result:
                legislation.result = LEGISLATION_RESULT[1][0]
            else:
                legislation.result = LEGISLATION_RESULT[2][0]
            legislation.save()




def set_status_of_akts():
    legislations = Legislation.objects.all()
    for legislation in legislations:
        votes = Vote.objects.filter(epa=legislation.epa)
        votes = votes.filter(motion__iregex=r'glasovanje o \w+ v celoti')
        if votes:
            if votes.count() > 1:
                print "FAIL"
                print votes.values_list("motion", flat=True)
                continue
            vote = votes[0]
            print vote.motion
            legislation.status = LEGISLATION_STATUS[1][0]
            if vote.result:
                legislation.result = LEGISLATION_RESULT[1][0]
            else:
                # zakon zavrnjen
                legislation.result = LEGISLATION_RESULT[2][0]
            legislation.save()

def set_accepted_laws():
    legislations = Legislation.objects.filter(procedure_phase__icontains='sprejet')
    for legislation in legislations:
        legislation.result = LEGISLATION_RESULT[1][0]
        legislation.status = LEGISLATION_STATUS[1][0]
        legislation.save()


def get_votes_without_legislation():
    v_e = set(list(Vote.objects.all().values_list("epa", flat=True)))
    l_e = list(Legislation.objects.all().values_list("epa", flat=True))
    print len(list((v_e-set(l_e)))) 


def hasLegislationLink(legislation):
    if legislation.sessions.all():
        return True
    else:
        return False


def getMotionClassification(motion): 
    classes = VOTE_INDICATORS
    text = motion.lower() 
    for cl, words in classes.items(): 
        for word in words: 
            if word.lower() in text: 
                return cl 

    return '14' # others


def recacheLegislationsOnSession(session_id):
    base_url = GLEJ_URL + '/'
    card_url = base_url + 'c/' + 'zakonodaja/:id?customUrl=http%3A%2F%2Fanalize.parlameter.si%2Fv1%2Fs%2FgetLegislationList%2F' + str(session_id) + '&forceRender=true'
    print card_url
    tryHard(card_url)
    card_url = base_url + 's/' + 'seznam-glasovanj/' + str(session_id) + '?forceRender=true'
    tryHard(card_url)
    votes = Vote.objects.filter(session__id_parladata=session_id)
    epas = votes.exclude(epa=None).distinct('epa').values_list('epa', flat=True)
    for epa in epas:
        if epa in [None, '']:
            continue
        card_url = base_url + 's/' + 'zakon/?customUrl=http%3A%2F%2Fanalize.parlameter.si%2Fv1%2Fs%2FgetLegislation%2F' + str(epa) + '&forceRender=true'
        print card_url
        tryHard(card_url)


def speech_the_order():
    sessions = Session.objects.all()
    for session in sessions:
    speeches_queryset = Speech.getValidSpeeches(datetime.now())
    speeches = speeches_queryset.filter(session=session).order_by("start_time",
                                                                  "agenda_item_order",
                                                                  "order")

    for i, s in enumetare(speeches):
        s.the_order = i
        s.save()