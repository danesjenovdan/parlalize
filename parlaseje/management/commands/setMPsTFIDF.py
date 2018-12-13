from django.core.management.base import BaseCommand, CommandError
from parlaseje.models import Session
from parlaposlanci.models import Person, Tfidf
from parlalize.utils_ import saveOrAbortNew, tryHard, getPersonData
from datetime import datetime
from parlalize.settings import SOLR_URL, API_URL

import requests
import json


def truncateTFIDF(data):
    """
    remove terms with to lowest frequency
    """
    newdata = []
    for term in data:
        if ' ' not in term['term']:
            if term['scores']['tf'] > 10:
                try:
                    float(term['term'])
                    pass
                except ValueError:
                    newdata.append(term)

    return newdata


def enrichPersonData(data, person_id):
    """
    make solr json preety and sort results by tf-idf
    """
    results = []

    for i, term in enumerate(data['termVectors'][1][3]):
        if i % 2 == 0:

            tkey = data['termVectors'][1][3][i]
            tvalue = data['termVectors'][1][3][i + 1]

            results.append({'term': tkey,
                            'scores': {tvalue[0]: tvalue[1],
                                       tvalue[2]: tvalue[3],
                                       tvalue[4]: tvalue[5]}})
            del data['termVectors'][1][3][i]
        else:
            del data['termVectors'][1][3][i]

    truncatedResults = truncateTFIDF(results)

    sortedResults = sorted(truncatedResults,
                           key=lambda k: k['scores']['tf-idf'],
                           reverse=True)[:25]

    enrichedData = {'person': getPersonData(person_id),
                    'results': sortedResults}

    return enrichedData


def setTfidfOfMP(commander, mp_id):
    url = '%s/tvrh/?q=id:p%s&tv.df=true&tv.tf=true&tv.tf_idf=true&wt=json&fl=id&tv.fl=content_t' % (
        SOLR_URL, mp_id)

    commander.stdout.write('About to fetch %s' % url)
    r = requests.get(url)

    commander.stdout.write('Saving speaker %s' % str(mp_id))
    try:
        output = enrichPersonData(r.json(), mp_id)

        date_of = datetime.now().date()
        person = Person.objects.get(id_parladata=output['person']['id'])
        saveOrAbortNew(Tfidf,
                       person=person,
                       created_for=date_of,
                       is_visible=False,
                       data=output['results'])
    except IndexError:
        commander.stderr.write('No data for this person, saving empty array.')
        date_of = datetime.now().date()
        person = Person.objects.get(id_parladata=mp_id)
        saveOrAbortNew(Tfidf,
                       person=person,
                       created_for=date_of,
                       is_visible=False,
                       data=[])


class Command(BaseCommand):
    help = 'Updates PresenceThroughTime'

    def add_arguments(self, parser):
        parser.add_argument(
            '--speaker_ids',
            nargs='+',
            help='Speaker parladata_id',
            type=int,
        )

    def handle(self, *args, **options):
        speaker_ids = []
        if options['speaker_ids']:
            speaker_ids = options['speaker_ids']
        else:
            self.stdout.write('Trying hard with %s/getMPs/' % API_URL)
            members = tryHard(API_URL + '/getMPs/').json()
            speaker_ids = [member['id'] for member in members]

        for speaker_id in speaker_ids:
            setTfidfOfMP(self, speaker_id)

        return 0
