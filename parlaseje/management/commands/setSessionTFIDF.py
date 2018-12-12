from django.core.management.base import BaseCommand, CommandError
from parlaseje.models import Session, Tfidf
from parlalize.utils_ import saveOrAbortNew
from datetime import datetime
from parlalize.settings import SOLR_URL

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

def enrichTFIDF(data):
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

    enrichedData = {'session': data['termVectors'][0].split('s')[1],
                    'results': sortedResults}

    return enrichedData

def setTfidfOfSession(commander, session_id):
    url = '%s/tvrh/?q=id:s%s&tv.df=true&tv.tf=true&tv.tf_idf=true&wt=json&fl=id&tv.fl=content_t' % (SOLR_URL, session_id)

    commander.stdout.write('About to fetch %s' % url)
    r = requests.get(url)

    commander.stdout.write('Saving session %s' % str(session_id))
    try:
        output = enrichTFIDF(r.json())

        date_of = datetime.now().date()
        session = Session.objects.get(id_parladata=output['session'])
        saveOrAbortNew(Tfidf,
                      session=session,
                      created_for=date_of,
                      is_visible=False,
                      data=output['results'])
    except IndexError:
        commander.stderr.write('No data for this session.')

class Command(BaseCommand):
    help = 'Updates PresenceThroughTime'

    def add_arguments(self, parser):
        parser.add_argument(
            '--session_ids',
            nargs='+',
            help='Session parladata_id',
            type=int,
        )

    def handle(self, *args, **options):
        ses_ids = []
        if options['session_ids']:
            ses_ids = options['session_ids']
        else:
            ses_ids = Session.objects.all().values_list('id_parladata', flat=True)
        
        for session_id in ses_ids:
          setTfidfOfSession(self, session_id)       

        return 0
