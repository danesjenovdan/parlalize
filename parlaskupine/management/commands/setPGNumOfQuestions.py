# TODO needs more output when calculating

import json

from collections import Counter

from django.core.management.base import BaseCommand, CommandError
from parlaposlanci.models import Person
from parlaskupine.models import Organization, NumberOfQuestions
from parlalize.utils_ import tryHard, saveOrAbortNew, getDataFromPagerApi, getPersonData
from datetime import datetime
from parlalize.settings import API_DATE_FORMAT, API_URL


class Command(BaseCommand):
    help = 'Updates compas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            nargs=1,
            help='Date for which to run the card',
        )

    def handle(self, *args, **options):
        if options['date']:
            date_ = options['date']
            date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
        else:
            date_ = datetime.now().date().strftime(API_DATE_FORMAT)
            date_of = datetime.now().date()

        self.stdout.write('Trying hard for %s/getAllQuestions/%s' % (API_URL, date_))
        url = API_URL + '/getAllQuestions/' + date_
        data = getDataFromPagerApi(url)
        self.stdout.write('Trying hard for %s/getAllPGs/%s' % (API_URL, date_))
        url_pgs = API_URL + '/getAllPGs/' + date_
        pgs_on_date = tryHard(url_pgs).json()
        self.stdout.write('Trying hard for %s/getMPs/%s' % (API_URL, date_))
        url = API_URL + '/getMPs/' + date_
        mps = tryHard(url).json()

        mpStatic = {}
        for mp in mps:
            mpStatic[str(mp['id'])] = getPersonData(str(mp['id']), date_)

        # self.stdout.write('Trying hard for %s/getAllPGsExt/%s' % (API_URL, date_))
        # allPGs = tryHard(API_URL+'/getAllPGsExt/').json().keys()

        pg_ids = [int(pg_id) for pg_id in pgs_on_date.keys()]
        authors = []
        for question in data:
            qDate = datetime.strptime(question['date'], '%Y-%m-%dT%X')
            qDate = qDate.strftime(API_DATE_FORMAT)
            for author in question['author_id']:
                try:
                    person_data = mpStatic[str(author)]
                except KeyError as e:
                    print(str(question['author_id']))
                    person_data = getPersonData(str(author), date_)
                    mpStatic[str(author)] = person_data
                if person_data and person_data['party'] and person_data['party']['id']:
                    authors.append(person_data['party']['id'])
                else:
                    print 'person nima mpstatic: ', author

        avg = len(authors)/float(len(pg_ids))
        question_count = Counter(authors)
        max_value = 0
        max_orgs = []
        for maxi in question_count.most_common(90):
            if max_value == 0:
                max_value = maxi[1]
            if maxi[1] == max_value:
                max_orgs.append(maxi[0])
            else:
                break
        is_saved = []
        for pg_id in pg_ids:
            org = Organization.objects.get(id_parladata=pg_id)
            is_saved.append(saveOrAbortNew(model=NumberOfQuestions,
                                        created_for=date_of,
                                        organization=org,
                                        score=question_count[pg_id],
                                        average=avg,
                                        maximum=max_value,
                                        maxOrgs=max_orgs))

        return 0
