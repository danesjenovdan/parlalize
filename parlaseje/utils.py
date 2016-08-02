# -*- coding: UTF-8 -*-
import numpy
from datetime import datetime, timedelta
from django.http import Http404
import requests
from parlalize.utils import saveOrAbortNew
from parlaposlanci.models import Person, LastActivity
from parlaskupine.models import Organization
from parlaseje.models import *
from parlalize.settings import VOTE_MAP, API_URL, BASE_URL, API_DATE_FORMAT
import requests


def getGraphCardModel(model, id, date=None):
    if date:
        modelObject = model.objects.filter(id_parladata=id, created_at__lte=datetime.strptime(date, '%d.%m.%Y'))
    else:
        modelObject = model.objects.filter(id_parladata=id, created_at__lte=datetime.now())
    if not modelObject:
        raise Http404("Nismo našli kartice")
    else:
        modelObject = modelObject.latest('created_at')
    return modelObject


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

def saveOrAbortMotion(model, **kwargs):
	savedModel = model.objects.filter(**kwargs)
	tab = []
	if savedModel:
		ids = Vote.objects.values('id_parladata')
		for i in ids:
			tab.append(i['id_parladata'])
		for a in savedModel:
			if a.id_parladata in tab:
				print "Not saved"
			else:
				newModel = model(**kwargs)
				newModel.save()
				print "Saved"
	else:
		newModel = model(**kwargs)
		newModel.save()
		print "Saved"

def saveOrAbortAbsent(model, **kwargs):
	tab = []
	value = kwargs['id_parladata']
	if model:
		ids = AbsentMPs.objects.values('id_parladata')
		for i in ids:
			tab.append(i['id_parladata'])
		if int(value) in tab:
			print "Not saved"
			return False
		else:
			newModel = model(**kwargs)
			newModel.save()
			print "Saved"
			return True
	else:
		newModel = model(**kwargs)
		newModel.save()
		print "Saved"

def saveOrAbortPres(model, **kwargs):
	savedModel = kwargs['id_parladata']
	tab = []
	if savedModel:
		ids = model.objects.values('id_parladata')
		for i in ids:
			tab.append(i['id_parladata'])
		if savedModel in tab:
			print "Not saved"
		else:
			newModel = model(**kwargs)
			newModel.save()
			print "Saved"
	else:
		newModel = model(**kwargs)
		newModel.save()
		print "Saved"
		
def countBallots(vote):
    # count votes for, against, abstentions, misses
    votesfor = len([ballot for ballot in vote.vote.all() if ballot.option == 'za'])
    votesagainst = len([ballot for ballot in vote.vote.all() if ballot.option == 'proti'])
    votesabstained = len([ballot for ballot in vote.vote.all() if ballot.option == 'kvorum'])
    votesmissing = len([ballot for ballot in vote.vote.all() if ballot.option == 'ni'])

    return {'for': votesfor, 'against': votesagainst, 'abstained': votesabstained, 'missing': votesmissing}

def updateVotes():
    for vote in Vote.objects.all():
        counts = countBallots(vote)

        votes_for = counts['for']
        against = counts['against']
        abstain = counts['abstained']
        not_present = counts['missing']

        # saveOrAbortNew(Vote, session=vote.session, motion=vote.motion, votes_for=votes_for, against=against, abstain=abstain, not_present=not_present, result=vote.result, id_parladata=vote.id_parladata, created_for=vote.created_for)
        vote.votes_for = votes_for
        vote.against = against
        vote.abstain = abstain
        vote.not_present = not_present
        vote.save()

    return 1

def getSesIDs(start_date, end_date):
	result = []
	data = requests.get(API_URL + '/getSessions/').json()
	session = Session.objects.filter(start_time__gte=start_date, start_time__lte=end_date)
	for ids in session:
		result.append(ids.id_parladata)
	return result

def getSesDates(end_date):
	result = []
	data = requests.get(API_URL + '/getSessions/').json()
	session = Session.objects.filter(start_time__lte=end_date)
	for ids in session:
		result.append(ids.start_time)
	return result

def getSesCardModelNew(model, id, date=None):
    if date:
        modelObject = model.objects.filter(session__id_parladata=id,
                                           created_for__lte=datetime.strptime(date, '%d.%m.%Y'))
    else:
        modelObject = model.objects.filter(session__id_parladata=id,
                                           created_for__lte=datetime.now())

    if not modelObject:
        #if model == LastActivity:
            #return None
        raise Http404("Nismo našli kartice")
    else:
        modelObject = modelObject.latest('created_for')
        print "get object BUBU", modelObject.created_for
    return modelObject

def resultOfMotion(votes_for, against, abstain, not_present):
	allMPs = 0.666666667 * (int(votes_for) + int(against) + int(abstain) + int(not_present))
	if votes_for < allMPs:
		allMPs = 0
		return False

	else:
		allMPs = 0
		return True