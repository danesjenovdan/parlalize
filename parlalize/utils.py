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
            if model != LastActivity and savedModel.latest('created_for').created_for != model.objects.filter(person__id_parladata=kwargs["person"].id_parladata, created_for__lte=created_for).latest("created_for").created_for:
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

def getSCardModel(model, id_se, date=None):
    if date:
        modelObject = model.objects.filter(id_parladata=id_se,
                                           created_at__lte=datetime.strptime(date, '%d.%m.%Y'))
    else:
        modelObject = model.objects.filter(id_parladata=id_se,
                                           created_at__lte=datetime.now())
    if not modelObject:
        raise Http404("Nismo našli kartice")
    else:
        modelObject = modelObject.latest('created_at')
    return modelObject

def updateOrganizations():
    data = requests.get(API_URL+'/getAllOrganizations').json()
    for pg in data:
        if Organization.objects.filter(id_parladata=pg):
            org = Organization.objects.get(id_parladata=pg)
            org.name = data[pg]['name']
            org.classification = data[pg]['classification']
            org.acronym = data[pg]['acronym']
            print data[pg]['acronym']
            org.save()
        else:
            org = Organization(name=data[pg]['name'],
                               classification=data[pg]['classification'],
                               id_parladata=pg,
                               acronym=data[pg]['acronym'])
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

#treba pofixsat
def updateMotionOfSession():
    ses = Session.objects.all()
    for s in ses:
        print s.id_parladata
        requests.get(BASE_URL+'/s/setMotionOfSession/'+str(s.id_parladata))

#treba pofixsat
def updateBallots():
    data = requests.get(API_URL+'/getAllBallots').json()
    existingISs = Ballot.objects.all().values_list("id_parladata", flat=True)
    for dic in data:
        if int(dic["id"]) not in existingISs:#Ballot.objects.filter(id_parladata=dic['id']):
            print "adding ballot " + str(dic['vote'])
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

    setAllSessions()
    print "Sessions"

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

            #print member, votes[str(member)].keys()
            # Print member and vote id where is fail in data for cutVotes
            for member in members:
                for b in votes_ids:
                    if str(b) not in votes[str(member)].keys():
                        print member, b, "FAIL"
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
        guest  = requests.get(API_URL + '/getPersonData/'+str(id_parladata)+'/').json()
        return {
                'type': "visitor" if guest else "unknown",
                'party': {
                          'acronym': None, 
                          'id': None, 
                          'name': None}, 
                'name': guest["name"] if guest else None, 
                'gov_id': None, 
                'id': id_parladata,
                'district': None,
                'gender': None,
                }
    return {
            'type': "mp",
            'name': data.person.name,
            'id': int(data.person.id_parladata),
            'gov_id': data.gov_id,
            'party': Organization.objects.get(id_parladata=data.party_id).getOrganizationData(),
            'gender':data.gender,
            'district': data.district
        }


def getPersonDataAPI(request, id_parladata, date_=None):
    data = getPersonData(id_parladata, date_)
    return JsonResponse(data)


def modelsData(request):
    out = []
    for ct in ContentType.objects.all():
        m = ct.model_class()
        
        out.append({"model":m.__module__,
                    "Ime modela":m.__name__,
                    "st:":m._default_manager.count()})
    return JsonResponse(out, safe=False)


def checkSessions():
    ses = requests.get(API_URL + '/getSessions/').json()
    sessions  = [s['id'] for s in ses]
    ballots = [s.vote.id_parladata for s in Ballot.objects.all()]
    motionIDs = []
    for id_se in sessions:
        if len(requests.get(API_URL + '/motionOfSession/'+str(id_se)+'/').json()) > 0:
            motionIDs.append(id_se)
    print "Vsa glasovanja: ", len(motionIDs)
    
    if len(Session.objects.all()) > 0:
        print "Seje katerih ni v parlalizah: ", list(set(sessions) - set(Session.objects.values_list('id_parladata', flat=True)))
    else:
        print "ni sej sploh"

    if len(Vote.objects.all()) > 0:
        print "Vote katerih ni v parlalizah: ", list(set(motionIDs) - set(Vote.objects.values_list('id_parladata', flat=True)))
    else:
        print "ni votov sploh"

    if len(Vote_graph.objects.all()) > 0:
        print "Vote graph katerih ni v parlalizah: ", list(set(motionIDs) - set(Vote_graph.objects.all().values_list('vote__id_parladata', flat=True)))
    else:
        print "ni votov grafov sploh"

    if len(PresenceOfPG.objects.all()) > 0:
        print "stevilo PresenceOfPG: ", len(PresenceOfPG.objects.all())
    else:
        print "ni PresenceOfPG sploh"

    if len(AverageSpeeches.objects.all()) > 0:
        print "stevilo AverageSpeeches: ", len(AverageSpeeches.objects.all())
    else:
        print "ni AverageSpeeches sploh"

    if len(AbsentMPs.objects.all()) > 0:
        print "stevilo AbsentMPs: ", len(AbsentMPs.objects.all())
    else:
        print "ni AbsentMPs sploh"


def checkPG():
    org = [int(i) for i in (requests.get(API_URL+'/getAllOrganizations').json()).keys()]
    pg = [int(i) for i in (requests.get(API_URL+'/getAllPGs').json()).keys()]

    if len(Organization.objects.all()) > 0:
        print "Organizacij katerih ni v parlalizah: ", list(set(org) - set(Organization.objects.values_list('id_parladata', flat=True)))
    else:
        print "ni sej sploh"

    if len(PGStatic.objects.all()) > 0:
        print "PGStatic: za te PG ni kartice: ", list(set(pg) - set(PGStatic.objects.values_list('organization__id_parladata', flat=True)))
    else:
        print "ni PGStatic sploh"

    if len(PercentOFAttendedSession.objects.all()) > 0:
        print "PercentOFAttendedSession: za te PG ni kartice: ", list(set(pg) - set(PercentOFAttendedSession.objects.values_list('organization__id_parladata', flat=True)))
    else:
        print "ni PercentOFAttendedSession sploh"

    if len(MPOfPg.objects.all()) > 0:
        print "MPOfPg: za te PG ni kartice: ", list(set(pg) - set(MPOfPg.objects.values_list('organization__id_parladata', flat=True)))
    else:
        print "ni MPOfPg sploh"

    if len(MostMatchingThem.objects.all()) > 0:
        print "MostMatchingThem: za te PG ni kartice: ", list(set(pg) - set(MostMatchingThem.objects.values_list('organization__id_parladata', flat=True)))
    else:
        print "ni MostMatchingThem sploh"

    if len(LessMatchingThem.objects.all()) > 0:
        print "LessMatchingThem: za te PG ni kartice: ", list(set(pg) - set(LessMatchingThem.objects.values_list('organization__id_parladata', flat=True)))
    else:
        print "ni LessMatchingThem sploh"

    if len(DeviationInOrganization.objects.all()) > 0:
        print "DeviationInOrganization: za te PG ni kartice: ", list(set(pg) - set(DeviationInOrganization.objects.values_list('organization__id_parladata', flat=True)))
    else:
        print "ni DeviationInOrganization sploh"

    if len(CutVotes.objects.all()) > 0:
        print "CutVotes: za te PG ni kartice: ", list(set(pg) - set(CutVotes.objects.values_list('organization__id_parladata', flat=True)))
    else:
        print "ni CutVotes sploh"

    if len(VocabularySize.objects.all()) > 0:
        print "VocabularySize: za te PG ni kartice: ", list(set(pg) - set(VocabularySize.objects.values_list('organization__id_parladata', flat=True)))
    else:
        print "ni VocabularySize sploh"

def checkMP():
    mps = [i['id'] for i in requests.get(API_URL+'/getMPs').json()]

    print mps

    if len(Person.objects.all()) > 0:
        print "Poslancev katerih ni v parlalizah: ", list(set(mps) - set(Person.objects.values_list('id_parladata', flat=True)))
    else:
        print "ni sej sploh"
    
    if len(Presence.objects.all()) > 0:
        print "Presence: za te MP ni kartice: ", list(set(mps) - set(Presence.objects.values_list('person__id_parladata', flat=True)))
    else:
        print "ni Presence sploh"

    if len(SpokenWords.objects.all()) > 0:
        print "SpokenWords: za te MP ni kartice: ", list(set(mps) - set(SpokenWords.objects.values_list('person__id_parladata', flat=True)))
    else:
        print "ni SpokenWords sploh"

    if len(SpeakingStyle.objects.all()) > 0:
        print "SpeakingStyle: za te MP ni kartice: ", list(set(mps) - set(SpeakingStyle.objects.values_list('person__id_parladata', flat=True)))
    else:
        print "ni SpeakingStyle sploh"

    #if len(CutVotes.objects.all()) > 0:
    #    print "CutVotes: za te MP ni kartice: ", list(set(mps) - set(CutVotes.objects.values_list('person__id_parladata', flat=True)))
    #else:
    #    print "ni CutVotes sploh"

    if len(LastActivity.objects.all()) > 0:
        print "LastActivity: za te MP ni kartice: ", list(set(mps) - set(LastActivity.objects.values_list('person__id_parladata', flat=True)))
    else:
        print "ni LastActivity sploh"

    if len(EqualVoters.objects.all()) > 0:
        print "EqualVoters: za te MP ni kartice: ", list(set(mps) - set(EqualVoters.objects.values_list('person__id_parladata', flat=True)))
    else:
        print "ni EqualVoters sploh"

    if len(LessEqualVoters.objects.all()) > 0:
        print "LessEqualVoters: za te MP ni kartice: ", list(set(mps) - set(LessEqualVoters.objects.values_list('person__id_parladata', flat=True)))
    else:
        print "ni LessEqualVoters sploh"

    if len(MPsWhichFitsToPG.objects.all()) > 0:
        print "MPsWhichFitsToPG: za te MP ni kartice: ", list(set(mps) - set(MPsWhichFitsToPG.objects.values_list('person__id_parladata', flat=True)))
    else:
        print "ni MPsWhichFitsToPG sploh"

    if len(MPStaticPL.objects.all()) > 0:
        print "MPStaticPL: za te MP ni kartice: ", list(set(mps) - set(MPStaticPL.objects.values_list('person__id_parladata', flat=True)))
    else:
        print "ni MPStaticPL sploh"
    #if len(MPStaticGroup.objects.all()) > 0:
    #    print "MPStaticGroup: za te MP ni kartice: ", list(set(mps) - set(MPStaticGroup.objects.values_list('person__id_parladata', flat=True)))
    #else:
    #    print "ni MPStaticGroup sploh"

    if len(NumberOfSpeechesPerSession.objects.all()) > 0:
        print "NumberOfSpeechesPerSession: za te MP ni kartice: ", list(set(mps) - set(NumberOfSpeechesPerSession.objects.values_list('person__id_parladata', flat=True)))
    else:
        print "ni NumberOfSpeechesPerSession sploh"

    #if len(VocabularySize.objects.all()) > 0:
    #    print "VocabularySize: za te MP ni kartice: ", list(set(mps) - set(VocabularySize.objects.values_list('person__id_parladata', flat=True)))
    #else:
    #    print "ni VocabularySize sploh"

    if len(AverageNumberOfSpeechesPerSession.objects.all()) > 0:
        print "AverageNumberOfSpeechesPerSession: za te MP ni kartice: ", list(set(mps) - set(AverageNumberOfSpeechesPerSession.objects.values_list('person__id_parladata', flat=True)))
    else:
        print "ni AverageNumberOfSpeechesPerSession sploh"

    #if len(Compass.objects.all()) > 0:
    #    print "Compass: za te MP ni kartice: ", list(set(mps) - set(Compass.objects.values_list('person__id_parladata', flat=True)))
    #else:
    #    print "ni Compass sploh"

    if len(TaggedBallots.objects.all()) > 0:
        print "TaggedBallots: za te MP ni kartice: ", list(set(mps) - set(TaggedBallots.objects.values_list('person__id_parladata', flat=True)))
    else:
        print "ni TaggedBallots sploh"

    if len(MembershipsOfMember.objects.all()) > 0:
        print "MembershipsOfMember: za te MP ni kartice: ", list(set(mps) - set(MembershipsOfMember.objects.values_list('person__id_parladata', flat=True)))
    else:
        print "ni MembershipsOfMember sploh"
