from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags
from parlalize.utils_ import tryHard
from parlaseje.models import Vote
from parlalize.utils_ import saveOrAbortNew, getAllStaticData
from datetime import datetime
from parlalize.settings import SOLR_URL

import requests
import json


def commit_to_solr(commander, output):
    url = SOLR_URL + '/update?commit=true'
    commander.stdout.write('About to commit %s votes to %s' % (str(len(output)), url))
    data = json.dumps(output)
    requests.post(url,
                  data=data,
                  headers={'Content-Type': 'application/json'})


class Command(BaseCommand):
    help = 'Upload votes to Solr'

    def handle(self, *args, **options):
        # get static data
        self.stdout.write('Getting all static data')
        static_data = json.loads(getAllStaticData(None).content)

        # get all votes
        self.stdout.write('Getting votes')
        votes = Vote.objects.all()

        i = 1
        output = []
        for vote in votes:
            output.append({
                'term': 'VIII',
                'type': 'vote',
                'id': 'vote_' + str(vote.id_parladata),
                'vote_id': vote.id_parladata,
                'session_id': vote.session.id_parladata,
                'session_json': json.dumps(static_data['sessions'][str(vote.session.id_parladata)]),
                'org_id': vote.session.organization.id_parladata,
                'start_time': vote.created_for.isoformat(),
                'content': vote.motion,
                'results_json': json.dumps({
                    'motion_id': vote.id_parladata,
                    'text': vote.motion,
                    'for': vote.votes_for,
                    'against': vote.against,
                    'abstain': vote.abstain,
                    'absent': vote.not_present,
                    'result': vote.result,
                    'is_outlier': False, # TODO: remove hardcoded 'False' when algoritem for is_outlier will be fixed. vote.is_outlier,
                    'has_outliers': vote.has_outlier_voters,
                }),
            })

            if i % 100 == 0:
                commit_to_solr(self, output)
                output = []

            i += 1

        if len(output):
            commit_to_solr(self, output)

        return 0
