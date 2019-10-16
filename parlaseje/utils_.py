# -*- coding: UTF-8 -*-
from datetime import datetime
from django.http import Http404
from parlaposlanci.models import LastActivity
from parlaseje.models import *
from parlalize.settings import API_DATE_FORMAT, LEGISLATION_STATUS, LEGISLATION_RESULT, VOTE_INDICATORS, GLEJ_URL
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


def getSessionDataAPI(requests, session_id):
    session = Session.objects.filter(id_parladata=session_id)

    if session:
        return JsonResponse(session[0].getSessionData())
    else:
        return JsonResponse({'name': 'unkonwn',
                             'date': 'unkonwn',
                             'id': 'unkonwn',
                             })


def set_status_of_laws():
    legislations = Legislation.objects.all()
    for legislation in legislations:
        votes = Vote.objects.filter(epa=legislation.epa)
        votes = votes.filter(motion__icontains='glasovanje o zakonu v celoti')
        if votes:
            if votes.count() > 1:
                print("FAIL")
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
                print("FAIL")
                print(votes.values_list("motion", flat=True))
                continue
            vote = votes[0]
            print(vote.motion)
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
    print(len(list((v_e-set(l_e)))))


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
            if word.lower() in text.lower():
                return cl

    return '14' # others


def speech_the_order():
    sessions = Speech.objects.filter(the_order=None).distinct('session').values_list('session_id')
    for session_id in sessions:
        speeches_queryset = Speech.getValidSpeeches(datetime.now())
        speeches = speeches_queryset.filter(session=session_id).order_by("start_time",
                                                                         "agenda_item_order",
                                                                         "order")
        for i, s in enumerate(speeches):
            s.the_order = i
            s.save()


def speech_the_order_pl():
    sessions = Session.objects.all()
    for session in sessions:
        print(session.name)
        speeches_queryset = Speech.getValidSpeeches(datetime.now())
        speeches = speeches_queryset.filter(session=session).order_by("start_time",
                                                                      "order")
        for i, s in enumerate(speeches):
            s.the_order = i
            s.save()
