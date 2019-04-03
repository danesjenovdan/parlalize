from django.core.management.base import BaseCommand, CommandError
from parlaseje.models import Session, PresenceOfPG
from parlalize.utils_ import saveOrAbortNew, tryHard, getDataFromPagerApi, getOrganizationsWithVoters
from datetime import datetime
from parlalize.settings import API_URL, NOT_PRESENT

from collections import Counter

import requests
import json


def setPresenceOfPG(commander, session_id):
    """ Stores presence of PGs on specific session
    """
    PGs = getOrganizationsWithVoters()

    url = API_URL + '/getBallotsOfSession/' + str(session_id) + '/'
    commander.stdout.write(
        'About to get data from pager API from %s' % str(url))
    votes = getDataFromPagerApi(url)

    counters_in = Counter([vote['pg_id']
                           for vote in votes if vote['option'] not in NOT_PRESENT])
    counters_out = Counter([vote['pg_id']
                            for vote in votes if vote['option'] in NOT_PRESENT])

    pgs = list(set(counters_in.keys() + counters_out.keys()))

    results = {}

    for pg in pgs:
        if not str(pg) in PGs:
            continue
        try:
            results[pg] = counters_in[pg] * 100 / \
                (counters_in[pg] + counters_out[pg])
        except:
            if pg in counters_in.keys():
                results[pg] = 100
            elif pg in counters_out.keys():
                results[pg] = 0
            else:
                commander.stderr.write(
                    'Something is wrong with PG %s' % str(pg))
    session = Session.objects.get(id_parladata=session_id)
    saveOrAbortNew(model=PresenceOfPG,
                   created_for=session.start_time,
                   presence=[results],
                   session=session)

    commander.stdout.write(
        'Successfully saved presence of PGs for session %s' % str(session_id))


class Command(BaseCommand):
    help = 'Updates Presence of PG at session'

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
            setPresenceOfPG(self, session_id)

        return 0
