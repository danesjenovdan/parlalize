# -*- coding: UTF-8 -*-
import numpy
from datetime import datetime, timedelta
from django.http import Http404
import requests
from parlaposlanci.models import Person, LastActivity, MPStaticPL
from parlaskupine.models import Organization
from parlaseje.models import Session, Vote, Speech, Session, Ballot
from parlalize.settings import VOTE_MAP, API_URL, BASE_URL
import requests
import json


def voteToLogical(vote):
    if vote == "za":
        return 1
    elif vote == "proti":
        return 0
    else:
        return -1


# Return dictionary of votes results by user ids.
def getLogicVotes(date_=None):
    if date_:
        r = requests.get(API_URL+'/getVotes/'+date_)
        v = requests.get(API_URL+'/getAllVotes/'+date_)
    else:
        r = requests.get(API_URL+'/getVotes/')
        v = requests.get(API_URL+'/getAllVotes/')
    pl_votes = v.json()
    votes = r.json()

    for person_id in votes.keys():
        for vote in pl_votes:
            try:
                votes[str(person_id)][str(vote["id"])] = VOTE_MAP[str(votes[str(person_id)][str(vote["id"])])]
            except:
                if type(votes[str(person_id)]) == list:
                    votes[str(person_id)] = {}
                votes[str(person_id)][str(vote["id"])] = VOTE_MAP['ni_poslanec']

    return votes


def getVotes():
    r = requests.get(API_URL+'/getVotes/')
    pl_votes = Vote.objects.all()
    votes = r.json()
    for person_id in votes.keys():
        for vote in pl_votes:
            try:
                if not votes[str(person_id)][str(vote.id_parladata)]:
                    print "bu"
            except:
                if type(votes[str(person_id)]) == list:
                    votes[str(person_id)] = {}
                votes[str(person_id)][str(vote.id_parladata)] = 'ni_poslanec'
    return votes


def votesToLogical(votes, length):
    maxVotes = length
    for key in votes.keys():
        votes[key] = map(voteToLogical, votes[key])
        #TODO
        #remove this when numbers of ballots are equals for each member
        #it's make equal size for all votes
        if (len(votes[key]) < length):
            votes[key].extend(numpy.zeros(maxVotes-int(len(votes[key]))))
        else:

            votes[key] = [votes[key][i] for i in range(length)]


def voteFor(vote):
    if vote == "za":
        return 1
    else:
        return 0


def voteAgainst(vote):
    if vote == "proti":
        return 1
    else:
        return 0


def voteAbstain(vote):
    if vote == "kvorum":
        return 1
    else:
        return 0


def voteAbsent(vote):
    if vote == "ni":
        return 1
    else:
        return 0


def normalize(val, max_):
    try:
        return round((float(val)*100)/float(max_))
    except:
        return val


#checks if cards with the data exists or not
def saveOrAbort(model, **kwargs):
    savedModel = model.objects.filter(**kwargs)
    if savedModel:
        #Add cards which has always uninqe data
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


# checks if cards with the data exists or not NEW
"""
usage:
    watch parlaposlanci/views.py:setMembershipsOfMember

    if you use saveOrAbortNew in setter you need to use getPersonCardModelNew in getter
"""
def saveOrAbortNew(model, **kwargs):
    def save_it(model, created_for, **kwargs):
        kwargs.update({'created_for': created_for})
        newModel = model(**kwargs)
        newModel.save()
        return True
    if model != LastActivity:
        created_for = kwargs.pop('created_for')
    print kwargs
    savedModel = model.objects.filter(**kwargs)
    if savedModel:
        if 'person' in kwargs:
            if savedModel.latest('created_for').created_for != model.objects.filter(person__id_parladata=kwargs["person"].id_parladata).latest("created_at").created_for and model != LastActivity:
                save_it(model, created_for, **kwargs)
        elif "organization" in kwargs:
            if savedModel.latest('created_for').created_for != model.objects.filter(organization__id_parladata=kwargs["organization"].id_parladata).latest("created_at").created_for:
                save_it(model, created_for, **kwargs)
    else:
        if model != LastActivity:
            kwargs.update({'created_for': created_for})
        newModel = model(**kwargs)
        newModel.save()
        return True
    return False


def findDatesFromLastCard(model, id, lastParsedDate):
    toDate = datetime.strptime(lastParsedDate, '%d.%m.%Y').date()
    print model._meta.app_label
    try:
        if model._meta.app_label == "parlaposlanci":
            lastCardDate = model.objects.filter(person__id_parladata=id).order_by("-created_for")[0].created_for
        elif model._meta.app_label == "parlaskupine":
            lastCardDate = model.objects.filter(organization__id_parladata=id).order_by("-created_for")[0].created_for
        elif model._meta.app_label == "parlaseje":
            lastCardDate = model.objects.filter(session__id_parladata=id).order_by("-created_for")[0].created_for
    except:
        lastCardDate = datetime.strptime("01.08.2014", '%d.%m.%Y').date()
    #lastCardDate = lastCardDate.replace(tzinfo=None)

    return [(lastCardDate+timedelta(days=days)) for days in range((toDate-lastCardDate).days)]


def getPersonCardModelNew(model, id, date=None):
    if date:
        modelObject = model.objects.filter(person__id_parladata=id, created_for__lte=datetime.strptime(date, '%d.%m.%Y'))
    else:
        modelObject = model.objects.filter(person__id_parladata=id, created_for__lte=datetime.now())

    if not modelObject:
        #if model == LastActivity:
            #return None
        raise Http404("Nismo našli kartice")
    else:
        if model == LastActivity:
            latest_day = modelObject.latest('created_for').created_for
            print latest_day
            if len(modelObject.filter(created_for=latest_day))>1:
                modelObject = modelObject.filter(created_for=latest_day).latest("created_at")
            else:
                modelObject = modelObject.latest('created_for')
        else:
            modelObject = modelObject.latest('created_for')
            print "get object BUBU", modelObject.created_for
    return modelObject


def getPersonCardModel(model, id, date=None):
    if date:
        if model == LastActivity:
            print date
            modelObject = model.objects.filter(person__id_parladata=id, date__lte=datetime.strptime(date, '%d.%m.%Y'))
        else:
            modelObject = model.objects.filter(person__id_parladata=id, created_at__lte=datetime.strptime(date, '%d.%m.%Y'))
    else:
        if model == LastActivity:
            modelObject = model.objects.filter(person__id_parladata=id, date__lte=datetime.now())
        else:
            modelObject = model.objects.filter(person__id_parladata=id, created_at__lte=datetime.now())
    if not modelObject:
        if model == LastActivity:
            return None
        raise Http404("Nismo našli kartice")
    else:
        if model == LastActivity:
            modelObject = modelObject.latest('date')
        else:
            modelObject = modelObject.latest('created_at')
    return modelObject


def updatePeople():
    data = requests.get(API_URL+'/getAllPeople/').json()
    mps = requests.get(API_URL+'/getMPs/').json()
    mps_ids = [mp['id'] for mp in mps]
    for mp in data:
        if Person.objects.filter(id_parladata=mp['id']):
            person = Person.objects.get(id_parladata=mp['id'])
            person.name = mp['name']
            person.pg = mp['membership']
            person.id_parladata = int(mp['id'])
            person.image = mp['image']
            person.actived = True if int(mp['id']) in mps_ids else False
            person.gov_id = mp['gov_id']
            person.save()
        else:
            person = Person(name=mp['name'], pg=mp['membership'], id_parladata=int(mp['id']), image=mp['image'], actived=True if int(mp['id']) in mps_ids else False, gov_id=mp['gov_id'])
            person.save()

    return 1


def getPGCardModel(model, id, date=None):
    if date:
        modelObject = model.objects.filter(organization__id_parladata=id,
                                           created_at__lte=datetime.strptime(date, '%d.%m.%Y'))
    else:
        modelObject = model.objects.filter(organization__id_parladata=id,
                                           created_at__lte=datetime.now())
    if not modelObject:
        raise Http404("Nismo našli kartice")
    else:
        modelObject = modelObject.latest('created_at')
    return modelObject


def getPGCardModelNew(model, id, date=None):
    if date:
        modelObject = model.objects.filter(organization__id_parladata=id,
                                           created_for__lte=datetime.strptime(date, '%d.%m.%Y'))
    else:
        modelObject = model.objects.filter(organization__id_parladata=id,
                                           created_for__lte=datetime.now())

    if not modelObject:
        #if model == LastActivity:
            #return None
        raise Http404("Nismo našli kartice")
    else:
        modelObject = modelObject.latest('created_for')
        print "get object BUBU", modelObject.created_for
    return modelObject


def updateOrganizations():
    data = requests.get(API_URL+'/getAllOrganizations').json()
    for pg in data:
        if Organization.objects.filter(id_parladata=pg):
            org = Organization.objects.get(id_parladata=pg)
            org.name = data[pg]['name']
            org.classification = data[pg]['classification']
        else:
            org = Organization(name=data[pg]['name'],
                               classification=data[pg]['classification'],
                               id_parladata=pg)
            org.save()
    return 1


def updateSpeeches():
    data = requests.get(API_URL+'/getAllSpeeches').json()
    existingISs = Speech.objects.all().values_list("id_parladata", flat=True)
    for dic in data:
        if int(dic["id"]) not in existingISs:
            print "adding speech"
            speech = Speech(person=Person.objects.get(id_parladata=int(dic['speaker'])),
                            organization=Organization.objects.get(id_parladata=int(dic['party'])),
                            content=dic['content'], order=dic['order'],
                            session=Session.objects.get(id_parladata=int(dic['session'])),
                            start_time=dic['start_time'],
                            end_time=dic['end_time'],
                            id_parladata=dic['id'])
            speech.save()
    return 1


def updateMotionOfSession():
    ses = Session.objects.all()
    for s in ses:
        print s.id_parladata
        requests.get(BASE_URL+'/s/setMotionOfSession/'+str(s.id_parladata))


def updateBallots():
    data = requests.get(API_URL+'/getAllBallots').json()
    existingISs = Ballot.objects.all().values_list("id_parladata", flat=True)
    for dic in data:
        if int(dic["id"]) not in existingISs:#Ballot.objects.filter(id_parladata=dic['id']):
            print "adding ballot"
            vote = Vote.objects.get(id_parladata=dic['vote'])
            ballots = Ballot(person=Person.objects.get(id_parladata=int(dic['voter'])),
                             option=dic['option'],
                             vote=vote,
                             start_time=vote.session.start_time,
                             end_time=None,
                             id_parladata=dic['id'])
            ballots.save()
    return 1


#def updateVotes():
#    data = requests.get(API_URL+'/getAllVotes').json()
#    for dic in data:
#        print dic['session'], dic['motion']
#        speeches = saveOrAbort(Vote, session=Session.objects.get(id_parladata=int(dic['session'])), motion=dic['motion'], organization=Organization.objects.get(id_parladata=int(dic['party'])), id_parladata=dic['id'], result=dic['result'], start_time=dic['start_time'])
#    return 1


def update():

    updateOrganizations()
    print "org"

    updatePeople()
    print "pep"

    result = requests.get(BASE_URL+'/s/setAllSessions/')
    print result

    updateSpeeches()
    print "speeches"

    updateMotionOfSession()
    print "votes"

    updateBallots()
    print "ballots"


# get all parliament member ID's
def getIDs():
    # create persons
    result = []

    data = requests.get(API_URL+'/getMPs/').json()

    for mp in data:
        result.append(mp['id'])

    return result


# get all PG ID's
def getPGIDs():
    data = requests.get(API_URL+'/getMembersOfPGs/').json()

    return [pg for pg in data]
