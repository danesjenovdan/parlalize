import requests
from parlaposlanci.views import setMPStaticPL
from parlalize.settings import API_URL, API_DATE_FORMAT
from datetime import datetime
from parlaposlanci.views import setCutVotes, setMPStaticPL, setMembershipsOfMember, setLessEqualVoters, setMostEqualVoters, setPercentOFAttendedSession, setLastActivity, setAverageNumberOfSpeechesPerSessionAll, setVocabularySizeAndSpokenWords, setCompass

from parlaposlanci.models import CutVotes, MPStaticPL, MembershipsOfMember, LessEqualVoters, EqualVoters, Presence, AverageNumberOfSpeechesPerSession, VocabularySize, Compass


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


def runSettersParlaposlanci(date_to):
    toDate = datetime.strptime(date_to, API_DATE_FORMAT).date()
    setters_models = {
        # model: setter,

        # CutVotes: setCutVotes,
        # MembershipsOfMember: setMembershipsOfMember,
        # LessEqualVoters: setLessEqualVoters,
        # EqualVoters: setMostEqualVoters,
        # Presence: setPercentOFAttendedSession,
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
                setter(None, str(membership["id"]), date.strftime('%d.%m.%Y'))
        # setLastActivity allways runs without date
        #setLastActivity(request, str(membership["id"]))

    # Runner for setters ALL
    all_in_one_setters_models = {
        # AverageNumberOfSpeechesPerSession: setAverageNumberOfSpeechesPerSessionAll,
        # VocabularySize: setVocabularySizeAndSpokenWords,
        # Compass: setCompass,
    }

    zero = datetime(day=2, month=8, year=2014).date()
    for model, setter in all_in_one_setters_models.items():
        print(toDate - datetime(day=2, month=8, year=2014).date()).days
        for i in range((toDate - datetime(day=2, month=8, year=2014).date()).days):
            print(zero + timedelta(days=i)).strftime('%d.%m.%Y')
            setter(None, (zero + timedelta(days=i)).strftime('%d.%m.%Y'))

    return JsonResponse({"status": "all is fine :D"}, safe=False)


# Create all cards for data_ date. If date_ is None set for run setters
# for today.
def onDateCardRunner(date_=None):
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    if date_:
        date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
    else:
        date_of = datetime.now().date()
        date_ = date_of.strftime(API_DATE_FORMAT)
    setters = [
        setCutVotes,
        setMPStaticPL,
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
