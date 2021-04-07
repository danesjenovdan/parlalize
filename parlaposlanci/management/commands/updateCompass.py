from django.core.management.base import BaseCommand, CommandError
from utils.compass import getData as getCompassData
from parlaskupine.models import Compass, Organization
from datetime import datetime
from django.conf import settings
from utils.parladata_api import getParentOrganizationsWithVoters


class Command(BaseCommand):
    help = 'Updates compas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            nargs=1,
            help='PG parladata_ids',
        )

    def handle(self, *args, **options):
        if options['date']:
            date_of = datetime.strptime(options['date'], settings.API_DATE_FORMAT).date()
        else:
            date_of = datetime.now().date()

        for org_id in getParentOrganizationsWithVoters():
            self.stdout.write('Organization: %s' % str(org_id))
            data = getCompassData(date_of, org_id)
            if data == []:
                self.stdout.write('No data for compass. Organization %s' % str(org_id))
            #print data

            existing_compas = Compass.objects.filter(created_for=date_of, organization__id_parladata=org_id)
            if existing_compas:
                existing_compas[0].data = data
                existing_compas[0].save()
            else:
                org = Organization.objects.get(id_parladata=org_id)
                Compass(created_for=date_of,
                        data=data,
                        organization=org).save()
            self.stdout.write('Compass was set.')
        return 0
