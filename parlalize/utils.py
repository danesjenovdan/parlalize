# -*- coding: UTF-8 -*-
import numpy
from datetime import datetime, timedelta
from django.http import Http404, JsonResponse
import requests
from parlaposlanci.models import *
from parlaskupine.models import *
from parlaseje.models import *
from parlalize.settings import VOTE_MAP, API_URL, BASE_URL, API_DATE_FORMAT, DEBUG
from django.contrib.contenttypes.models import ContentType
import requests
import json
import numpy as np



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
    #print kwargs
    savedModel = model.objects.filter(**kwargs)
    if savedModel:
        if 'person' in kwargs:
            if savedModel.latest('created_for').created_for != model.objects.filter(person__id_parladata=kwargs["person"].id_parladata).latest("created_at").created_for and model != LastActivity:
                save_it(model, created_for, **kwargs)
        elif "organization" in kwargs:
            if savedModel.latest('created_for').created_for != model.objects.filter(organization__id_parladata=kwargs["organization"].id_parladata).latest("created_at").created_for:
                save_it(model, created_for, **kwargs)
        elif "session" in kwargs:
            if savedModel.latest('created_for').created_for != model.objects.filter(session__id_parladata=kwargs["session"].id_parladata).latest("created_at").created_for:
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
        if model._meta.app_label == "parlaposlanci":
            lastCardDate = model.objects.filter(person__id_parladata=id).order_by("-created_for")[0].created_for
        elif model._meta.app_label == "parlaskupine":
            lastCardDate = model.objects.filter(organization__id_parladata=id).order_by("-created_for")[0].created_for
        elif model._meta.app_label == "parlaseje":
            lastCardDate = model.objects.all().order_by("-created_for")[0].created_for
    except:
        lastCardDate = datetime.strptime("02.08.2014", '%d.%m.%Y').date()
    #lastCardDate = lastCardDate.replace(tzinfo=None)
    if not lastCardDate:
        if minDate:
            lastCardDate = datetime.strptime(minDate, '%d.%m.%Y').date()
        else:
            lastCardDate = datetime.strptime("02.08.2014", '%d.%m.%Y').date()
    return [(lastCardDate+timedelta(days=days)) for days in range((toDate-lastCardDate).days)]


def getPersonCardModelNew(model, id, date=None):
    if date:
        modelObject = model.objects.filter(person__id_parladata=id, created_for__lte=datetime.strptime(date, '%d.%m.%Y'))
    else:
        modelObject = model.objects.filter(person__id_parladata=id, created_for__lte=datetime.now())

    if not modelObject:
        #if model == LastActivity:
            #return None
        if DEBUG:
            raise Http404("Nismo našli kartice"+ str(model)+str(id))
        else:
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


# get all parliament member ID's
def getIDs():
    # create persons
    result = []
    #getAllPeople
    data = requests.get(API_URL+'/getAllPeople').json()
    #data = requests.get(API_URL+'/getMPs').json()

    for mp in data:
        result.append(mp['id'])

    return result


# get all PG ID's
def getPGIDs():
    data = requests.get(API_URL+'/getMembersOfPGs/').json()

    return [pg for pg in data]


def getRangeVotes(pgs, date_, votes_type="logic"):
    print date_
    def getVotesOnDay(votesPerDay_, day):
        #tempList = sorted(votesPerDay_, key=lambda k: k['time'])
        if day in votesPerDay_.keys():
            votesPerDay_[day].sort(key=lambda r: r["time"])
        else:
            return []
        try:
            out = [a["id"] for a in votesPerDay_[day]]
            return out
        except:
            return []

    #get data
    r = requests.get(API_URL+'/getMembersOfPGsOnDate/'+date_)
    membersInPGs = r.json()

    r = requests.get(API_URL+'/getMembersOfPGsRanges/'+date_)
    membersInPGsRanges = r.json()

    #create dict votesPerDay
    r = requests.get(API_URL+'/getAllVotes/'+date_)
    allVotesData = r.json()

    if date_:
        if votes_type=="logic":
            votes = getLogicVotes(date_)
        else:
            r = requests.get(API_URL+'/getVotes/'+date_)
            votes = r.json()

        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        if votes_type=="logic":
            votes = getLogicVotes()
        else:
            r = requests.get(API_URL+'/getVotes/'+date_)
            votes = r.json()
        date_of = datetime.now().date()

    #print votes
    #prepare votes in "windows"
    votesPerDay = {}
    for vote in allVotesData:
        vote_date = vote["start_time"].split("T")[0]
        if vote_date in votesPerDay.keys():
            votesPerDay[vote_date].append({"id": vote["id"], "time": datetime.strptime(vote["start_time"], "%Y-%m-%dT%X")})
        else:
            votesPerDay[vote_date] = [{"id": vote["id"], "time": datetime.strptime(vote["start_time"], "%Y-%m-%dT%X")}]

    # get average score of PG
    if votes_type=="logic":
        pg_score=np.array([])
    else:
        pg_score=[]
    counter = 0
    all_votes = []
    for membersInRange in membersInPGsRanges:
        start_date = datetime.strptime(membersInRange["start_date"], API_DATE_FORMAT).date()
        end_date = datetime.strptime(membersInRange["end_date"], API_DATE_FORMAT).date()
        days = (end_date - start_date).days
        votes_ids = [vote_id for i in range(days+1) for vote_id in getVotesOnDay(votesPerDay, (start_date+timedelta(days=i)).strftime("%Y-%m-%d"))]
        if votes_ids==[]:
            continue
        all_votes = all_votes + votes_ids
        counter+=len(votes_ids)
        if votes_type=="logic":
            pg_score_temp = np.mean([[votes[str(member)][str(b)]
                                    for b in votes_ids]
                                    for pg_id in pgs for member in membersInRange["members"][pg_id]],
                                    axis=0)
        else:
            members = [member for pg_id in pgs for member in membersInRange["members"][pg_id]]
        
            pg_score_temp =[votes[str(member)][str(b)] for member in members for b in votes_ids]

        if votes_type=="logic":
            pg_score = np.concatenate((pg_score,pg_score_temp), axis=0)
        else:
            pg_score = pg_score+pg_score_temp

    return pg_score, membersInPGs, votes, all_votes



def getMPGovId(id_parladata):
    person = Person.objects.filter(id_parladata=id_parladata)[0]
    out = {"id":person.id_parladata, "gov_id":person.gov_id}
    return out


def getPersonData(id_parladata, date_=None):
    if not date_:
        date_ = datetime.now().strftime(API_DATE_FORMAT)
    try:
        data = getPersonCardModelNew(MPStaticPL, id_parladata, date_)
    except:
        return {
                'party': {
                          'acronym': 'unknown', 
                          'id': 'unknown', 
                          'name': 'unknown'}, 
                'name': 'unknown_'+str(id_parladata), 
                'gov_id': 'unknown_'+str(id_parladata), 
                'id': id_parladata}
    return {
            'name': data.person.name,
            'id': int(data.person.id_parladata),
            'gov_id': data.gov_id,
            'party': Organization.objects.get(id_parladata=data.party_id).getOrganizationData(),
            'gender':data.gender
        }


def getPersonDataAPI(request, id_parladata, date_=None):
    if not date_:
        date_ = datetime.now().strftime(API_DATE_FORMAT)
    data = getPersonCardModelNew(MPStaticPL, id_parladata, date_)
    return JsonResponse({
            'name': data.person.name,
            'id': int(data.person.id_parladata),
            'gov_id': data.gov_id,
            'party': Organization.objects.get(id_parladata=data.party_id).getOrganizationData(),
            'gender':data.gender
        })


def modelsData(request):
    out = []
    for ct in ContentType.objects.all():
        m = ct.model_class()
        out.append({"model":m.__module__,
                    "Ime modela":m.__name__,
                    "st:":m._default_manager.count()})
    return JsonResponse(out, safe=False)
