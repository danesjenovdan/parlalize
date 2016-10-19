import requests
from parlaposlanci.views import setMPStaticPL
from parlalize.settings import API_URL, API_DATE_FORMAT, BASE_URL
from parlalize.utils import getPGIDs, findDatesFromLastCard
from datetime import datetime, timedelta
from django.apps import apps
from parlaposlanci.models import District
from raven.contrib.django.raven_compat.models import client


from parlaposlanci.views import setCutVotes, setMPStaticPL, setMembershipsOfMember, setLessEqualVoters, setMostEqualVoters, setPercentOFAttendedSession, setLastActivity, setAverageNumberOfSpeechesPerSessionAll, setVocabularySizeAndSpokenWords, setCompass
from parlaposlanci.models import Person, CutVotes, VocabularySize, MPStaticPL, MembershipsOfMember, LessEqualVoters, EqualVoters, Presence, AverageNumberOfSpeechesPerSession, VocabularySize, Compass

from parlaskupine.views import setCutVotes as setCutVotesPG, setDeviationInOrg, setLessMatchingThem, setMostMatchingThem, setPercentOFAttendedSessionPG, setMPsOfPG, setBasicInfOfPG, setWorkingBodies, setVocabularySizeALL
from parlaskupine.models import Organization, WorkingBodies, CutVotes as CutVotesPG, DeviationInOrganization, LessMatchingThem, MostMatchingThem, PercentOFAttendedSession, MPOfPg, PGStatic

from parlaseje.models import Session, Vote, Ballot, Speech

from multiprocessing import Pool

## parlalize initial runner methods ##

def updatePeople():
    data = requests.get(API_URL + '/getAllPeople/').json()
    mps = requests.get(API_URL + '/getMPs/').json()
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
            person = Person(name=mp['name'], pg=mp['membership'], id_parladata=int(mp['id']), image=mp[
                            'image'], actived=True if int(mp['id']) in mps_ids else False, gov_id=mp['gov_id'])
            person.save()

    return 1


def updateOrganizations():
    data = requests.get(API_URL + '/getAllOrganizations').json()
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
    data = requests.get(API_URL + '/getAllSpeeches').json()
    existingISs = list(Speech.objects.all().values_list("id_parladata", flat=True))
    print existingISs
    for dic in data:
        if int(dic["id"]) not in existingISs and str(dic["id"]) not in existingISs:
            print "adding speech"
            speech = Speech(person=Person.objects.get(id_parladata=int(dic['speaker'])),
                            organization=Organization.objects.get(
                                id_parladata=int(dic['party'])),
                            content=dic['content'], order=dic['order'],
                            session=Session.objects.get(
                                id_parladata=int(dic['session'])),
                            start_time=dic['start_time'],
                            end_time=dic['end_time'],
                            id_parladata=dic['id'])
            speech.save()
    return 1

# treba pofixsat


def updateMotionOfSession():
    ses = Session.objects.all()
    for s in ses:
        print s.id_parladata
        requests.get(BASE_URL + '/s/setMotionOfSession/' + str(s.id_parladata))

# treba pofixsat


def updateBallots():
    data = requests.get(API_URL + '/getAllBallots').json()
    existingISs = Ballot.objects.all().values_list("id_parladata", flat=True)
    for dic in data:
        # Ballot.objects.filter(id_parladata=dic['id']):
        if int(dic["id"]) not in existingISs:
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


def setAllSessions():
    data  = requests.get(API_URL + '/getSessions/').json()
    session_ids = list(Session.objects.all().values_list("id_parladata", flat=True))
    for sessions in data:
        if sessions['id'] not in session_ids:
            result = Session(name=sessions['name'],
                             gov_id=sessions['gov_id'],
                             start_time=sessions['start_time'],
                             end_time=sessions['end_time'],
                             classification=sessions['classification'],
                             id_parladata=sessions['id'],
                             organization=Organization.objects.get(id_parladata=sessions['organization_id']),
                             ).save()
        else:
            if not Session.objects.filter(name=sessions['name'],
                                          gov_id=sessions['gov_id'],
                                          start_time=sessions['start_time'],
                                          end_time=sessions['end_time'],
                                          classification=sessions['classification'],
                                          id_parladata=sessions['id'],
                                          organization=Organization.objects.get(id_parladata=sessions['organization_id']),):
                #save changes
                session = Session.objects.get(id_parladata=sessions['id'])
                session.name = sessions['name']
                session.gov_id = sessions['gov_id']
                session.start_time = sessions['start_time']
                session.end_time = sessions['end_time']
                session.classification = sessions['classification']
                session.id_parladata = sessions['id']
                session.organization = Organization.objects.get(id_parladata=sessions['organization_id'])
                session.save()

    return 1

## parlaposlanci runner methods ##


def updateMPStatic():
    memberships = requests.get(API_URL + '/getMembersOfPGsRanges/').json()
    lastObject = {"members": {}}
    print "[info] update MP static"
    for change in memberships:
        # call setters for new pg
        for pg in list(set(change["members"].keys()) - set(lastObject["members"].keys())):
            for member in change["members"][pg]:
                setMPStaticPL(None, str(member), change["start_date"])

        # call setters for members which have change in memberships
        for pg in change["members"].keys():
            if pg in lastObject["members"].keys():
                for member in list(set(change["members"][pg]) - set(lastObject["members"][pg])):
                    setMPStaticPL(None, str(member), change["start_date"])
        lastObject = change


def runSettersMP(date_to):
    toDate = datetime.strptime(date_to, API_DATE_FORMAT).date()
    setters_models = {
        # model: setter,

        CutVotes: setCutVotes,
        MembershipsOfMember: setMembershipsOfMember,
        LessEqualVoters: setLessEqualVoters,
        EqualVoters: setMostEqualVoters,
        Presence: setPercentOFAttendedSession,

    }
    memberships = requests.get(API_URL + '/getAllTimeMemberships').json()

    for membership in memberships:
        if membership["end_time"]:
            end_time = datetime.strptime(
                membership["end_time"].split("T")[0], "%Y-%m-%d").date()
            if end_time > toDate:
                end_time = toDate
        else:
            end_time = toDate

        for model, setter in setters_models.items():
            print setter, date_to
            if membership["start_time"]:
                print "START", membership["start_time"]
                start_time = datetime.strptime(
                    membership["start_time"].split("T")[0], "%Y-%m-%d")
                dates = findDatesFromLastCard(model, membership["id"], end_time.strftime(
                    API_DATE_FORMAT), start_time.strftime(API_DATE_FORMAT))
            else:
                dates = findDatesFromLastCard(
                    model, membership["id"], end_time.strftime(API_DATE_FORMAT))
            for date in dates:
                print date.strftime('%d.%m.%Y')
                print str(membership["id"]) + "/" + date.strftime('%d.%m.%Y')
                try:
                    setter(None, str(membership["id"]), date.strftime('%d.%m.%Y'))
                except:
                    client.captureException()
        # setLastActivity allways runs without date
        setLastActivity(request, str(membership["id"]))

    # Runner for setters ALL
    all_in_one_setters_models = {
        AverageNumberOfSpeechesPerSession: setAverageNumberOfSpeechesPerSessionAll,
        VocabularySize: setVocabularySizeAndSpokenWords,
        Compass: setCompass,
    }

    zero = datetime(day=2, month=8, year=2014).date()
    for model, setter in all_in_one_setters_models.items():
        print(toDate - datetime(day=2, month=8, year=2014).date()).days
        for i in range((toDate - datetime(day=2, month=8, year=2014).date()).days):
            print(zero + timedelta(days=i)).strftime('%d.%m.%Y')
            try:
                setter(None, (zero + timedelta(days=i)).strftime('%d.%m.%Y'))
            except:
                client.captureException()

    return JsonResponse({"status": "all is fine :D"}, safe=False)

#for membership in memberships:
def doMembersRunner(data):
    membership = data["membership"]
    toDate = data["toDate"]
    setters_models = data["setters_models"]
    if membership["end_time"]:
        end_time = datetime.strptime(
            membership["end_time"].split("T")[0], "%Y-%m-%d").date()
        if end_time > toDate:
            end_time = toDate
    else:
        end_time = toDate

    for model, setter in setters_models.items():
        print setter, toDate
        if membership["start_time"]:
            #print "START", membership["start_time"]
            start_time = datetime.strptime(
                membership["start_time"].split("T")[0], "%Y-%m-%d")
            dates = findDatesFromLastCard(model, membership["id"], end_time.strftime(
                API_DATE_FORMAT), start_time.strftime(API_DATE_FORMAT))
        else:
            dates = findDatesFromLastCard(
                model, membership["id"], end_time.strftime(API_DATE_FORMAT))
        for date in dates:
            #print date.strftime('%d.%m.%Y')
            #print str(membership["id"]) + "/" + date.strftime('%d.%m.%Y')
            try:
                setter(None, str(membership["id"]), date.strftime('%d.%m.%Y'))
            except:
                client.captureException()
    # setLastActivity allways runs without date
        setLastActivity(None, str(membership["id"]))


#for model, setter in all_in_one_setters_models.items():
def doAllMembersRunner(data):
    setter = data["setters"]
    model = data["model"]
    toDate = data["toDate"]
    zero = data["zero"]
    #print(toDate - datetime(day=2, month=8, year=2014).date()).days

    members = requests.get(API_URL + '/getMPs/' + toDate.strftime(API_DATE_FORMAT)).json()
    dates = []
    if model == Compass:
        cards = model.objects.all().order_by("created_for")
        if cards:
            dates.append(list(cards)[-1].created_for)
    else:
        for member in members:
            members_cards = model.objects.filter(person__id_parladata=member["id"]).order_by("created_for")
            if members_cards:
                dates.append(list(members_cards)[-1].created_for)
    print dates
    if dates:
        zero = min(dates)
    print zero
    print "start all members"+str(setter)
    for i in range((toDate - zero).days):
        print(zero + timedelta(days=i)).strftime('%d.%m.%Y')
        try:
            setter(None, (zero + timedelta(days=i)).strftime('%d.%m.%Y'))
        except:
            client.captureException()

def runSettersMPMultiprocess(date_to):
    toDate = datetime.strptime(date_to, API_DATE_FORMAT).date()
    zero = datetime(day=2, month=8, year=2014).date()
    setters_models = {
        # model: setter,

        CutVotes: setCutVotes,
        MembershipsOfMember: setMembershipsOfMember,
        LessEqualVoters: setLessEqualVoters,
        EqualVoters: setMostEqualVoters,
        Presence: setPercentOFAttendedSession,

    }

    # Runner for setters ALL
    all_in_one_setters_models = {
        AverageNumberOfSpeechesPerSession: setAverageNumberOfSpeechesPerSessionAll,
        VocabularySize: setVocabularySizeAndSpokenWords,
        Compass: setCompass,
    }

    memberships = requests.get(API_URL + '/getAllTimeMemberships').json()



    pool = Pool(processes=16)
    pool.map(doMembersRunner, [{"membership": membership, "toDate": toDate, "setters_models": setters_models} for membership in memberships])

    pool = Pool(processes=16)
    pool.map(doAllMembersRunner, [{"setters": setter, "model": model, "toDate": toDate, "zero": zero} for model, setter in all_in_one_setters_models.items()])

    

    

    return JsonResponse({"status": "all is fine :D"}, safe=False)


# Create all cards for data_ date. If date_ is None set for run setters
# for today.
def onDateMPCardRunner(date_=None):
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = (datetime.now()-timedelta(days=1)).date()
        date_ = date_of.strftime(API_DATE_FORMAT)
    setters = [
        setCutVotes,
        setMembershipsOfMember,
        setLessEqualVoters,
        setMostEqualVoters,
        setPercentOFAttendedSession,
    ]

    memberships = requests.get(API_URL + '/getMPs/' + date_).json()

    for membership in memberships:
        for setter in setters:
            print "running:" + str(setter)
            try:
                setter(None, str(membership["id"]), date_)
            except:
                print FAIL + "FAIL on: " + str(setter) + " and with id: " + str(membership["id"]) + ENDC
        setLastActivity(None, str(membership["id"]))

    # Runner for setters ALL
    all_in_one_setters = [
        setAverageNumberOfSpeechesPerSessionAll,
        setVocabularySizeAndSpokenWords,
        setCompass,
    ]

    zero = datetime(day=2, month=8, year=2014).date()
    for setter in all_in_one_setters:
        print "running:" + str(setter)
        try:
            setter(None, date_)
        except:
            print "FAIL on: " + str(setter)


## parlaseje runners methods ##

def runSettersPG(request, date_to):
    toDate = datetime.strptime(date_to, '%d.%m.%Y').date()
    setters_models = {
        CutVotesPG: setCutVotesPG,#BASE_URL+'/p/setCutVotes/',
        DeviationInOrganization: setDeviationInOrg,
        LessMatchingThem: setLessMatchingThem,
        MostMatchingThem: setMostMatchingThem,
        PercentOFAttendedSession: setPercentOFAttendedSessionPG,
        MPOfPg: setMPsOfPG,
        PGStatic: setBasicInfOfPG,
    }

    IDs = getPGIDs()
    #IDs = [1, 2]
    # print IDs
    allIds = len(IDs)
    curentId = 0

    for model, setter in setters_models.items():
        for ID in IDs:
            print setter
            membersOfPGsRanges = requests.get(
                API_URL + '/getMembersOfPGRanges/' + str(ID) + ("/" + date_to if date_to else "/")).json()
            start_time = datetime.strptime(
                membersOfPGsRanges[0]["start_date"], '%d.%m.%Y').date()
            end_time = datetime.strptime(
                membersOfPGsRanges[-1]["end_date"], '%d.%m.%Y').date()
            dates = findDatesFromLastCard(model, ID, date_to)
            print dates
            for date in dates:
                if date < start_time or date > end_time:
                    break
                print date.strftime(API_DATE_FORMAT)
                # print setter + str(ID) + "/" + date.strftime(API_DATE_FORMAT)
                setter(request, str(ID), date.strftime(API_DATE_FORMAT))
        curentId += 1
        # result = requests.get(setter + str(ID) + "/" + date.strftime(API_DATE_FORMAT)).status_code

    # Runner for setters ALL
    all_in_one_setters_models = {
        VocabularySize: setVocabularySizeALL,
    }

    zero = datetime(day=2, month=8, year=2014).date()
    for model, setter in all_in_one_setters_models.items():
        print(toDate - datetime(day=2, month=8, year=2014).date()).days
        for i in range((toDate - datetime(day=2, month=8, year=2014).date()).days):
            print(zero + timedelta(days=i)).strftime('%d.%m.%Y')
            setter(request, (zero + timedelta(days=i)).strftime('%d.%m.%Y'))

    organizations = requests.get(
        API_URL + "/getOrganizatonByClassification").json()
    print organizations
    for org in organizations["working_bodies"] + organizations["council"]:
        print org
        dates = findDatesFromLastCard(WorkingBodies, org["id"], date_to)
        for date in dates:
            print setWorkingBodies(request, str(org["id"]), date.strftime(API_DATE_FORMAT)).content

    return JsonResponse({"status": "all is fine :D"}, safe=False)


def onDatePGCardRunner(date_=None):
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = (datetime.now()-timedelta(days=1)).date()
        date_ = date_of.strftime(API_DATE_FORMAT)
    print date_
    setters = [
        setCutVotesPG,
        setDeviationInOrg,
        setLessMatchingThem,
        setMostMatchingThem,
        setPercentOFAttendedSessionPG,
        setMPsOfPG,
        setBasicInfOfPG,
    ]

    membersOfPGsRanges = requests.get(
        API_URL + '/getMembersOfPGsRanges/' + date_).json()
    IDs = [key for key, value in membersOfPGsRanges[-1]["members"].items()
           if value]
    curentId = 0

    for setter in setters:
        for ID in IDs:
            print setter
            try:
                setter(None, str(ID), date_)
            except:
                print FAIL + "FAIL on: " + str(setter) + " and with id: " + str(ID) + ENDC

    # Runner for setters ALL
    all_in_one_setters = [
        setVocabularySizeALL,
    ]

    for setter in all_in_one_setters:
        try:
            setter(None, date_)
        except:
            print FAIL + "FAIL on: " + str(setter) + ENDC

    organizations = requests.get(
        API_URL + "/getOrganizatonByClassification").json()
    for org in organizations["working_bodies"] + organizations["council"]:
        print "set working_bodie: " + str(org["id"])
        try:
            setWorkingBodies(None, str(org["id"]), date_)
        except:
            print FAIL + "FAIL on: " + "setWorkingBodies" + " and with id: " + str(org["id"]) + ENDC

    return True


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

    updateDistricts()

    updateMPStatic()

    #onDateMPCardRunner()

    #onDatePGCardRunner()


def deleteAppModels(appName):
    my_app = apps.get_app_config(appName)
    my_models = my_app.get_models()
    for model in my_models:
        print "delete model: ", model
        model.objects.all().delete()


def updateDistricts():
    districts = requests.get(API_URL + "/getDistricts").json()
    for district in districts:
        if not District.objects.filter(name=district):
            District(name=district).save()
    return 1
