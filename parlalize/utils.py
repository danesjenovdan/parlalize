# -*- coding: UTF-8 -*-
import numpy
from datetime import datetime, timedelta
from django.http import Http404
import requests
from parlaposlanci.models import Person, LastActivity
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


def getLogicVotes():
    r = requests.get(API_URL+'/getVotes/')
    pl_votes = Vote.objects.all()
    votes = r.json()
    for person_id in votes.keys():
        for vote in pl_votes:
            try:
                votes[str(person_id)][str(vote.id_parladata)] = VOTE_MAP[votes[str(person_id)][str(vote.id_parladata)]]
            except:
                if type(votes[str(person_id)]) == list:
                    votes[str(person_id)] = {}
                votes[str(person_id)][str(vote.id_parladata)] = VOTE_MAP['ni_poslanec']

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
    if vote == "ni":
        return 1
    else:
        return 0


def normalize(val, max):
    try:
        return round((val*100)/float(max))
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
            person.save()
        else:
            person = Person(name=mp['name'], pg=mp['membership'], id_parladata=int(mp['id']), image=mp['image'], actived=True if int(mp['id']) in mps_ids else False)
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


def updateOrganizations():
    data = requests.get(API_URL+'/getAllOrganizations').json()
    for pg in data:
        if Organization.objects.filter(id_parladata=pg['id']):
            org = Organization.objects.get(id_parladata=pg['id'])
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
                             start_time=vote.start_time,
                             end_time=None,
                             id_parladata=dic['id'])
            ballots.save()
    return 1

"""
def updateVotes():
    data = requests.get(API_URL+'/getAllVotes').json()
    for dic in data:
        print dic['session'], dic['motion']
        speeches = saveOrAbort(Vote, session=Session.objects.get(id_parladata=int(dic['session'])), motion=dic['motion'], organization=Organization.objects.get(id_parladata=int(dic['party'])), id_parladata=dic['id'], result=dic['result'], start_time=dic['start_time'])
    return 1"""


def update():
    
    updateOrganizations()
    print "org"
    
    updatePeople()
    print "pep"
    
    result = requests.get(BASE_URL+'/s/setAllSessions/')
    print result
    
    updateSpeeches()
    print "speeches"
    
    #updateVotes() TODO JURIĆ'S UPDATE VOTES -> pokliči setMotionOfSession za vsako sejo
    print "votes"
    
    updateBallots()
    print "ballots"
