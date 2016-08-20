# -*- coding: UTF-8 -*-
from datetime import datetime

from parlalize.utils import *
import requests
import json
from django.http import JsonResponse
from parlaseje.models import *
from parlalize.settings import API_URL, API_DATE_FORMAT
from parlaseje.utils import *
from collections import defaultdict
from math import fabs
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

# Create your views here.

def getSpeech(request, speech_id):
    speech = Speech.objects.get(id_parladata=speech_id)
    out={"speech_id":speech.id_parladata, "content":speech.content}
    result = {
        'person': {
            'name': speech.person.name,
            'id': int(speech.person.id_parladata)
        },
        'results': out
    }
    return JsonResponse(result)

def getSessionSpeeches(request, session_id):
    out = []
    session = Session.objects.get(id_parladata=session_id)
    for speech in Speech.objects.filter(session=session).order_by("-start_time"):
        out.append({"speech_id": speech.id_parladata, "content": speech.content, "person_id": speech.person.id_parladata})
    result = {
        'session': {
            'name': session.name,
            'id': int(session.id_parladata)
        },
        'results': out
    }
    return JsonResponse(result, safe=False)

def setMotionOfSession(request, id_se):
    motion  = requests.get(API_URL + '/motionOfSession/'+str(id_se)+'/').json()
    session = Session.objects.get(id_parladata=id_se)
    tab = []
    yes = 0
    no = 0
    kvorum = 0
    not_present = 0
    option = ""
    tabyes = []
    tabno = []
    tabkvo = []
    tabnp = []
    yesdic = defaultdict(int)
    nodic = defaultdict(int)
    kvordic = defaultdict(int)
    npdic = defaultdict(int)
    tyes = []
    for mot in motion:
        votes  = requests.get(API_URL + '/getVotesOfMotion/'+str(mot['vote_id'])+'/').json()
        for vote in votes:
            if vote['option'] == str('za'):
                yes = yes + 1
                yesdic[vote['pg_id']] += 1
                tabyes.append(vote['mp_id'])
            if vote['option'] == str('proti'):
                no = no + 1
                nodic[vote['pg_id']] += 1
                tabno.append(vote['mp_id'])

            if vote['option'] == str('kvorum'):
                kvorum = kvorum + 1
                kvordic[vote['pg_id']] += 1
                tabkvo.append(vote['mp_id'])
            if vote['option'] == str('ni'):
                not_present = not_present + 1
                npdic[vote['pg_id']] += 1
                tabnp.append(vote['mp_id'])

        if Vote.objects.filter(id_parladata=mot['vote_id']):
            Vote.objects.filter(id_parladata=mot['vote_id']).update(created_for=session.start_time,
                                                                    session=Session.objects.get(id_parladata=int(id_se)),
                                                                    motion=mot['text'],
                                                                    tags=mot['tags'],
                                                                    votes_for=yes,
                                                                    against=no,
                                                                    abstain=kvorum,
                                                                    not_present=not_present,
                                                                    result=resultOfMotion(yes, no, kvorum,not_present),
                                                                    id_parladata=mot['vote_id'],
                                                                    id_parladata_session=int(id_se))
        else:
            result = saveOrAbortNew(model=Vote,
                                       created_for=session.start_time,
                                       session=Session.objects.get(id_parladata=int(id_se)),
                                       motion=mot['text'],
                                       tags=mot['tags'],
                                       votes_for=yes,
                                       against=no,
                                       abstain=kvorum,
                                       not_present=not_present,
                                       result=resultOfMotion(yes, no, kvorum,not_present),
                                       id_parladata=mot['vote_id'],
                                       id_parladata_session=int(id_se)
                                       )



        yes = 0
        no = 0
        kvorum = 0
        not_present = 0
        tabyes = []
        tabno = []
        tabkvo = []
        tabnp = []
        yesdic = defaultdict(int)
        nodic = defaultdict(int)
        kvordic = defaultdict(int)
        npdic = defaultdict(int)
    return JsonResponse({'alliswell': True})

def setMotionOfSessionGraph(request, id_se):
    motion  = requests.get(API_URL + '/motionOfSession/'+str(id_se)+'/').json()
    session = Session.objects.get(id_parladata=id_se)
    tab = []
    yes = 0
    no = 0
    kvorum = 0
    not_present = 0
    option = ""
    tabyes = []
    tabno = []
    tabkvo = []
    tabnp = []
    yesdic = defaultdict(int)
    nodic = defaultdict(int)
    kvordic = defaultdict(int)
    npdic = defaultdict(int)
    tyes = []
    for mot in motion:
        votes  = requests.get(API_URL + '/getVotesOfMotion/'+str(mot['vote_id'])+'/').json()
        for vote in votes:
            if vote['option'] == str('za'):
                yes = yes + 1
                yesdic[vote['pg_id']] += 1
                tabyes.append(vote['mp_id'])
            if vote['option'] == str('proti'):
                no = no + 1
                nodic[vote['pg_id']] += 1
                tabno.append(vote['mp_id'])

            if vote['option'] == str('kvorum'):
                kvorum = kvorum + 1
                kvordic[vote['pg_id']] += 1
                tabkvo.append(vote['mp_id'])
            if vote['option'] == str('ni'):
                not_present = not_present + 1
                npdic[vote['pg_id']] += 1
                tabnp.append(vote['mp_id'])

        vg = saveOrAbortNew(model=Vote_graph,
                         session=Session.objects.get(id_parladata=int(id_se)),
                         created_for=session.start_time,
                         motion=mot['text'],
                         votes_for=yes,
                         against=no,
                         abstain=kvorum,
                         not_present=not_present,
                         result=resultOfMotion(yes, no, kvorum,not_present),
                         id_parladata=mot['id'],
                         pgs_yes=yesdic,
                         pgs_no=nodic,
                         pgs_np=npdic,
                         pgs_kvor=kvordic,
                         mp_yes=tabyes,
                         mp_no=tabno,
                         mp_np=tabnp,
                         mp_kvor=tabkvo
                         )

        yes = 0
        no = 0
        kvorum = 0
        not_present = 0
        tabyes = []
        tabno = []
        tabkvo = []
        tabnp = []
        yesdic = defaultdict(int)
        nodic = defaultdict(int)
        kvordic = defaultdict(int)
        npdic = defaultdict(int)
    return JsonResponse({'alliswell': True})

def getMotionOfSession(request, id_se, date=False):
    out = []
    if Vote.objects.filter(session__id_parladata=id_se):
        if date:
            model = Vote.objects.filter(session__id_parladata=id_se, start_time__lte=datetime.strptime(date, '%d.%m.%Y'))
        else:
            model = Vote.objects.filter(session__id_parladata=id_se)

        for card in model:
            out.append({
            'session': {

                'name': Session.objects.get(id_parladata=int(id_se)).name,
                'date': Session.objects.get(id_parladata=int(id_se)).start_time.date(),
                'id': int(id_se)
            },
            'results': {

                    'motion_id': card.id_parladata,
                    'text': card.motion,
                    'votes_for': card.votes_for,
                    'against': card.against,
                    'abstain': card.abstain,
                    'not_present':card.not_present,
                    'result':card.result
            }
        })
    else:
        return JsonResponse({"status": "No card MOFO"}, safe=False)
    return JsonResponse(out, safe=False)


def getMotionGraph(request, id_mo, date=False):
    out = []
    if Vote_graph.objects.filter(id_parladata=id_mo):
        if date:
            model = Vote_graph.objects.filter(id_parladata=id_mo, start_time__lte=datetime.strptime(date, '%d.%m.%Y'))
        else:
            model = Vote_graph.objects.filter(id_parladata=id_mo)


    option_for = []
    option_kvor = []
    option_against = []
    option_np = []
    breakdown = []
    mps =[]


    for pg in model[0].pgs_kvor:
        party = Organization.objects.get(id_parladata=pg).getOrganizationData()

        for mp in model[0].mp_kvor:
            persondata = getPersonData(mp, date))

            if persondata['party']['acronym'] == party['acronym']:
                mps.append(persondata)

        option_kvor.append({'pg': party, 'mps': mps})

        mps = []

        out_kvor = {'option':'kvorum','total_votes': model[0].abstain, 'breakdown':option_kvor}

    for pg in model[0].pgs_yes:
        party = Organization.objects.get(id_parladata=pg).getOrganizationData()

        for mp in model[0].mp_yes:
            persondata = getPersonData(mp, date))

            if persondata['party']['acronym'] == party['acronym']:
                mps.append(persondata)

        option_for.append({'pg': party, 'mps': mps})

        mps = []

        out_for = {'option':'za','total_votes': model[0].votes_for, 'breakdown':option_for}

    for pg in model[0].pgs_no:
        party = Organization.objects.get(id_parladata=pg).getOrganizationData()
        for mp in model[0].mp_no:
            persondata = getPersonData(mp, date))

            if persondata['party']['acronym'] == party['acronym']:
                mps.append(persondata)

        option_against.append({'pg': party, 'mps': mps})

        mps = []

        out_against = {'option':'proti','total_votes': model[0].against, 'breakdown':option_against}

    for pg in model[0].pgs_np:
        party = Organization.objects.get(id_parladata=pg).getOrganizationData()
        for mp in model[0].mp_np:
            persondata = getPersonData(mp, date))

            if persondata['party']['acronym'] == party['acronym']:
                mps.append(persondata)

        option_np.append({'pg': party, 'mps': mps})

        mps = []

        out_np = {'option':'odsotni','total_votes': model[0].not_present, 'breakdown':option_np}

    out = {'id':id_mo, 'name': model[0].motion, 'result':model[0].result, 'required':'62', 'all': {'kvorum': out_kvor, 'for': out_for, 'against': out_against, 'not_present': out_np}}
    return JsonResponse(out, safe=False)

def setAbsentMPs(request, id_se):
    votes = requests.get(API_URL + '/getVotesOfSession/'+str(id_se)+'/').json()
    session = Session.objects.get(id_parladata=id_se)
    mps = requests.get(API_URL+'/getMembersOfPGsOnDate/'+ session.start_time.strftime(API_DATE_FORMAT)).json()


    mpsID = []
    if len(votes) != 0:
        mpsID = reduce(lambda x,y: x+y,mps.values())
        for vote in votes:
            if vote['option'] != 'ni':
                if vote['mp_id'] in mpsID:
                    mpsID.remove(vote['mp_id'])

        result = saveOrAbortNew(model=AbsentMPs,
                                id_parladata=id_se,
                                absentMPs=mpsID,
                                created_for=session.start_time
                                )

        mpsID = []
    return JsonResponse({'alliswell': True})


def getAbsentMPs(request, id_se, date=False):
    try:
        if date:
            date_ = datetime.strptime(date, API_DATE_FORMAT)
            ids = AbsentMPs.objects.get(id_parladata=int(id_se), start_time__lte=data_).absentMPs
        else:
            ids = AbsentMPs.objects.get(id_parladata=int(id_se)).absentMPs
            date_ = datetime.now().date()
            date = date_.strftime(API_DATE_FORMAT)
        results = []

        for abMP in ids:
            result = {
            "person": getPersonData(abMP, date)
            }
            results.append(result)

    except ObjectDoesNotExist:
        return JsonResponse({"status": "No card MOFO"}, safe=False)
    return JsonResponse(results, safe=False)

def setPresenceOfPG(request, id_se):
    votes = requests.get(API_URL+'/getVotesOfSession/'+str(id_se)+'/').json()
    motions = requests.get(API_URL+'/motionOfSession/'+str(id_se)+'/').json()
    session = Session.objects.get(id_parladata=id_se)
    membersOfPG = requests.get(API_URL+'/getMembersOfPGsOnDate/'+ session.start_time.strftime(API_DATE_FORMAT)).json()

    onSession = {}
    yesdic = defaultdict(int)
    allsessionsinone = defaultdict(list)
    final = {}
    numOfMPs = {}
    results = {}
    allPgs = {}

    if len(votes) != 0:
        for vote in votes:
            if vote['option'] != 'ni':
                if vote['mo_id'] in onSession.keys():
                    onSession[vote['mo_id']].append(vote['pg_id'])
                else:
                    onSession.update({vote['mo_id'] : [vote['pg_id']]})

    for i in membersOfPG:
        allPgs[i] = len(membersOfPG[i]) * len(motions)

    for b in onSession:
        for i in onSession[b]:
            yesdic[i] += 1
        results[b] = yesdic

    if len(results)>0:
        temp = dict(results[results.keys()[0]])
        for i in temp:
            if allPgs[str(i)] != 0:
                final[i] = int((float(temp[i]) / float(allPgs[str(i)])) * 100)


        result = saveOrAbortNew(model=PresenceOfPG,
                                created_for=session.start_time,
                                presence=[final],
                                id_parladata = int(id_se)
                                )

    return JsonResponse({'alliswell': True})

def getPresenceOfPG(request, id_se, date=False):

    results = []
    try:
        if date:
            presence = PresenceOfPG.objects.get(id_parladata=id_se, start_time__lte=datetime.strptime(date, '%d.%m.%Y'))
        else:
            presence = PresenceOfPG.objects.get(id_parladata=id_se)

            for p in presence.presence[0]:
                results.append({"id":Organization.objects.get(id_parladata=p).id_parladata, "name":Organization.objects.get(id_parladata=p).name, "percent":presence.presence[0][p], "acronym":Organization.objects.get(id_parladata=p).acronym})
    except ObjectDoesNotExist:
        return JsonResponse({"status": "No card MOFO"}, safe=False)
    return JsonResponse(results, safe=False)

def setSpeechesOnSession(request, date=False):
    if date:
        numberOfSessions = len(Session.objects.filter(start_time__lte=datetime.strptime(date, '%d.%m.%Y')))
        mps = requests.get(API_URL+'/getMPs/'+ date).json()
    else:
        numberOfSessions = len(Session.objects.filter(start_time__lte=datetime.now().date()).json())
        mps = requests.get(API_URL+'/getMPs/'+  str(datetime.now().date().strftime(API_DATE_FORMAT))).json()
        date = datetime.now().date()

    mpsID = {}
    for mp in mps:
        speech = len(requests.get(API_URL+'/getSpeechesOfMP/'+ str(mp['id'])+'/'+ date).json())
        if numberOfSessions !=0:
            mpsID.update({mp['id']:float(float(speech)/float(numberOfSessions))})
    date = datetime.strptime(date, '%d.%m.%Y')
    result = saveOrAbortNew(model=AverageSpeeches,
                                created_for=date,
                                speechesOnSession=mpsID
                                )
    return JsonResponse({'alliswell': True})


def getMinSpeechesOnSession(request, date=False):
    results = []
    try:
        if date:
            date_ = datetime.strptime(date, API_DATE_FORMAT)
            averageSpeeches = AverageSpeeches.objects.get(created_for=date_).speechesOnSession
        else:
            averageSpeeches = AverageSpeeches.objects.get().speechesOnSession
            date_ = datetime.now().date()
            date = date_.strftime(API_DATE_FORMAT)
        sort = sorted(averageSpeeches.items(), key=lambda x:x[1])

        for s in sort:
            result = {
                "person": getPersonData(s[0], date),
                'speeches': s[1]
            }
            results.append(result)
    except ObjectDoesNotExist:
        return JsonResponse({"status": "No card MOFO"}, safe=False)
    return JsonResponse(results[:5], safe=False)


def getMaxSpeechesOnSession(request, date=False):
    results = []
    try:
        if date:
            date_ = datetime.strptime(date, API_DATE_FORMAT)
            averageSpeeches = AverageSpeeches.objects.get(created_for=date_).speechesOnSession
        else:
            averageSpeeches = AverageSpeeches.objects.get().speechesOnSession
            date_ = datetime.now().date()
            date = date_.strftime(API_DATE_FORMAT)


        sort = sorted(averageSpeeches.items(), key=lambda x:x[1], reverse=True)
        for s in sort:
            result = {
                "person": getPersonData(s[0], date),
                'speeches': s[1]
            }
            results.append(result)

    except ObjectDoesNotExist:
        return JsonResponse({"status": "No card MOFO"}, safe=False)
    return JsonResponse(results[:5], safe=False)



def updateTags(request):
    tags = requests.get(API_URL+'/getTags').json()
    existing_tags = Tag.objects.all().values_list("name", flat=True)
    count = 0
    for tag in tags:
        if tag not in existing_tags:
            Tag(name=tag).save()
            count += 1
    return JsonResponse({'alliswell': True, "add_tags": count})


def setQuote(request, speech_id, start_pos, end_pos):
    speech = get_object_or_404(Speech, id_parladata=speech_id)
    quote = Quote(speech=speech, first_char=start_pos, last_char=end_pos, quoted_text=speech.content[int(start_pos):int(end_pos)])
    quote.save()

    return JsonResponse({"status": "alliswell", "id": quote.id})


def getQuote(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)

    return JsonResponse({"quoted_text": quote.quoted_text,
                         "start_idx": quote.first_char,
                         "end_idx": quote.last_char,
                         "speech_id": quote.speech.id_parladata})

def runSetters(request, date_to):


    setters_models = {
        #Vote: setMotionOfSession,
        #PresenceOfPG: setPresenceOfPG,
        #AbsentMPs: setAbsentMPs,
        #AverageSpeeches: setSpeechesOnSession,
        #Vote_graph: setMotionOfSessionGraph
    }
    for model, setter in setters_models.items():
        dates = findDatesFromLastCard(model, None, date_to)
        if dates==[]:
            continue
        if model != AverageSpeeches:
            IDs = getSesIDs(dates[1],dates[-1])
            for ID in IDs:
                setter(request, str(ID))
        else:
            datesSes = getSesDates(dates[-1])
            for date in datesSes:
                setter(request, date.strftime(API_DATE_FORMAT))
    return JsonResponse({"status": "all is fine :D"}, safe=False)
