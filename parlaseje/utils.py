# -*- coding: UTF-8 -*-
import numpy
from datetime import datetime, timedelta
from django.http import Http404
import requests
from parlaposlanci.models import Person, LastActivity
from parlaskupine.models import Organization
from parlaseje.models import Session, Vote, Speech, Session, Ballot, Vote_graph, Vote
from parlalize.settings import VOTE_MAP, API_URL, BASE_URL
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
	