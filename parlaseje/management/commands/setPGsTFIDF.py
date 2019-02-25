from django.core.management.base import BaseCommand, CommandError
from parlaskupine.models import Organization, Tfidf
from parlalize.utils_ import saveOrAbortNew, tryHard
from parlaskupine.utils_ import getPgData
from datetime import datetime
from parlalize.settings import SOLR_URL, API_URL, API_DATE_FORMAT

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


def enrichPGData(data, pg_id):
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

    enrichedData = {'organization': getPgData(pg_id),
                    'results': sortedResults}

    return enrichedData


def setTfidfOfPG(commander, pg_id):
    url = '%s/tvrh/?q=id:pgms_%s&tv.df=true&tv.tf=true&tv.tf_idf=true&wt=json&fl=id&tv.fl=content' % (
        SOLR_URL, pg_id)

    commander.stdout.write('About to fetch %s' % url)
    r = requests.get(url)

    commander.stdout.write('Saving PG %s' % str(pg_id))
    try:
        output = enrichPGData(r.json(), pg_id)

        date_of = datetime.now().date()
        organization = Organization.objects.get(
            id_parladata=output['organization']['id'])
        saveOrAbortNew(Tfidf,
                       organization=organization,
                       created_for=date_of,
                       is_visible=False,
                       data=output['results'])
    except IndexError:
        commander.stderr.write('No data for this PG, saving empty array.')
        date_of = datetime.now().date()
        organization = Organization.objects.get(
            id_parladata=pg_id)
        saveOrAbortNew(Tfidf,
                       organization=organization,
                       created_for=date_of,
                       is_visible=False,
                       data=[])


class Command(BaseCommand):
    help = 'Updates PresenceThroughTime'

    def add_arguments(self, parser):
        parser.add_argument(
            '--organization_ids',
            nargs='+',
            help='Organization parladata_id',
            type=int,
        )

    def handle(self, *args, **options):
        date_of = datetime.now().date()
        date_ = date_of.strftime(API_DATE_FORMAT)

        organization_ids = []
        if options['organization_ids']:
            organization_ids = options['organization_ids']
        else:
            self.stdout.write(
                'Trying hard with %s/getMembersOfPGsRanges/' % API_URL)
            url = API_URL + '/getMembersOfPGsRanges/' + date_
            membersOfPGsRanges = tryHard(url).json()
            organization_ids = [
                key for key, value in membersOfPGsRanges[-1]['members'].items()]

        for organization_id in organization_ids:
            setTfidfOfPG(self, organization_id)

        return 0
