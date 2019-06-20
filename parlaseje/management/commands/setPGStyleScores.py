from django.core.management.base import BaseCommand, CommandError
from parlaskupine.models import Organization, StyleScores
from parlalize.utils_ import saveOrAbortNew, tryHard, getPersonData
from utils.parladata_api import getOrganizationsWithVoters, getParentOrganizationsWithVoters
from datetime import datetime
from parlalize.settings import SOLR_URL, API_URL, API_DATE_FORMAT
from collections import Counter

from kvalifikatorji.scripts import problematicno, privzdignjeno, preprosto

import requests
import json


def getCountList(commander, pg_id, date_):
    """
    pg_id: id of the organization
    date_: date of analysis

    method return term frequency for each word spoken by speaker
    """
    data = None

    commander.stdout.write('Trying hard for %s/tvrh/?q=id:pgms_%s&tv.df=true&tv.tf=true&tv.tf_idf=true&wt=json&fl=id&tv.fl=content' % (SOLR_URL, str(pg_id)))
    data = tryHard(
        '%s/tvrh/?q=id:pgms_%s&tv.df=true&tv.tf=true&tv.tf_idf=true&wt=json&fl=id&tv.fl=content' % (SOLR_URL, str(pg_id))).json()

    results = []

    try:
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

        wordlist = {word["term"]: word["scores"]["tf"] for word in results}
    except IndexError:
        commander.stderr.write('No data for this organization, saving empty object.')
        wordlist = {}

    return wordlist


def getScores(words_list, counter, total):
    """
    word_list: list of words for each classificator (problematicno,
    privzdignjeno, preprosto)
    counter: counter of words for classfication
    total: counter of unique words

    method returns dictionary with score for each classificator
    """

    print 'Getting style scores'

    scores = {'problematicno': 0, 'privzdignjeno': 0, 'preprosto': 0}

    for word in counter:
        scores['problematicno'] = scores['problematicno'] + \
            words_list[0].setdefault(word, 0)
        scores['privzdignjeno'] = scores['privzdignjeno'] + \
            words_list[1].setdefault(word, 0)
        scores['preprosto'] = scores['preprosto'] + \
            words_list[2].setdefault(word, 0)

    if float(total) == 0.0:
        total = 1

    scores['problematicno'] = scores['problematicno']*1000000000/float(total)
    scores['privzdignjeno'] = scores['privzdignjeno']*1000000000/float(total)
    scores['preprosto'] = scores['preprosto']*1000000000/float(total)

    return scores


class Command(BaseCommand):
    help = 'Updates PresenceThroughTime'

    def handle(self, *args, **options):
        date_of = datetime.now().date()
        date_ = date_of.strftime(API_DATE_FORMAT)

        for org in getParentOrganizationsWithVoters():

            self.stdout.write('getting organizations with voters')
            organization_ids = getOrganizationsWithVoters(date_=date_of)

            scores = {}
            for organization_id in organization_ids:

                self.stdout.write('Org id: %s' % str(organization_id))
                # get word counts with solr
                counter = Counter(getCountList(self, int(organization_id), date_))
                total = sum(counter.values())

                scores_local = getScores([problematicno, privzdignjeno, preprosto],
                                        counter,
                                        total)

                self.stdout.write('Outputting scores_local: %s' %
                                str(scores_local))
                scores[organization_id] = scores_local

            self.stdout.write('Outputting scores: %s' % str(scores))
            average = {"problematicno": sum([score['problematicno']
                                            for score
                                            in scores.values()])/len(scores),
                    "privzdignjeno": sum([score['privzdignjeno']
                                            for score
                                            in scores.values()])/len(scores),
                    "preprosto": sum([score['preprosto']
                                        for score
                                        in scores.values()])/len(scores)}
            data = []
            for org_id, score in scores.items():
                data.append({'org': org_id,
                            'problematicno': score['problematicno'],
                            'privzdignjeno': score['privzdignjeno'],
                            'preprosto': score['preprosto'],
                            'problematicno_average': average['problematicno'],
                            'privzdignjeno_average': average['privzdignjeno'],
                            'preprosto_average': average['preprosto']})

            for score in data:
                self.stdout.write('About to save %s' % str(score))
                status = saveOrAbortNew(StyleScores,
                                        organization=Organization.objects.get(
                                            id_parladata=int(score['org'])),
                                        created_for=date_of,
                                        problematicno=float(
                                            score['problematicno']),
                                        privzdignjeno=float(
                                            score['privzdignjeno']),
                                        preprosto=float(score['preprosto']),
                                        problematicno_average=float(
                                            score['problematicno_average']),
                                        privzdignjeno_average=float(
                                            score['privzdignjeno_average']),
                                        preprosto_average=float(
                                            score['preprosto_average'])
                                        )
                self.stdout.write('SaveOrAbort status: %s' % str(status))

        return 0
