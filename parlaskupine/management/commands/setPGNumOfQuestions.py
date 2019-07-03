# TODO needs more output when calculating

import json

from collections import Counter

from django.core.management.base import BaseCommand, CommandError
from parlaposlanci.models import Person
from parlaskupine.models import Organization, NumberOfQuestions
from parlalize.utils_ import (tryHard, saveOrAbortNew, getDataFromPagerApi, getPersonData)
from utils.parladata_api import getOrganizationsWithVoters, getVotersIDs, getParentOrganizationsWithVoters, getQuestions
from datetime import datetime
from parlalize.settings import API_DATE_FORMAT, API_URL, DZ


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

        data = getQuestions()

        for org_id in getParentOrganizationsWithVoters():
            pgs_on_date = getOrganizationsWithVoters(date_=date_of, organization_id=org_id)
            mps = getVotersIDs(date_=date_of, organization_id=org_id)

            mpStatic = {}
            for mp in mps:
                mpStatic[str(mp)] = getPersonData(str(mp), date_)

            pg_ids = pgs_on_date
            authors = []
            for question in data:
                qDate = datetime.strptime(question['date'], '%Y-%m-%dT%X')
                qDate = qDate.strftime(API_DATE_FORMAT)
                for author in question['authors']:
                    try:
                        person_data = mpStatic[str(author)]
                    except KeyError as e:
                        print(str(question['authors']))
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
