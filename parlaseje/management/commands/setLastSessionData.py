from django.core.management.base import BaseCommand
from parlaseje.models import Session
from datetime import datetime

from parlaseje.management.commands.setLastSessionData import setPresenceOfPG
from parlaseje.management.commands.setLastSessionData import uploadSessionToSolr
from parlaseje.management.commands.setTfidfOfSession import setTfidfOfSession


def setLastSessionData(commander, session_id):
    """ Stores presence of PGs on specific session
    """
    setPresenceOfPG(commander, session_id)
    uploadSessionToSolr(commander, [session_id])
    setTfidfOfSession(commander, session_id)

    commander.stdout.write(
        'Successfully update data for last session %s' % str(session_id))

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
            setLastSessionData(self, session_id)

        return 0
