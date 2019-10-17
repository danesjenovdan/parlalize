
from django.core.management.base import BaseCommand, CommandError
from parlalize.utils_ import tryHard
from parlaskupine.models import Organization
from parlaseje.models import Session
from parlalize.settings import API_URL, DZ
from utils.parladata_api import setSessions

class Command(BaseCommand):
    help = 'Sets session data'

    def handle(self, *args, **options):
        self.stdout.write('Fetching data from %s/sessions/' % API_URL)
        data = getSessions()
        session_ids = list(Session.objects.all().values_list('id_parladata',
                                                            flat=True))
        for session in data:
            self.stdout.write('Setting session %s' % str(session['id']))
            orgs = Organization.objects.filter(id_parladata__in=session['organizations'])
            if not orgs:
                orgs = Organization.objects.filter(id_parladata=session['organization'])
            if session['id'] not in session_ids:
                self.stdout.write('New session %s' % str(session['id']))
                result = Session(name=session['name'],
                                gov_id=session['gov_id'],
                                start_time=session['start_time'],
                                end_time=session['end_time'],
                                classification=session['classification'],
                                id_parladata=session['id'],
                                in_review=session['in_review'],
                                organization=orgs[0]
                                )
                result.save()
                orgs = list(orgs)
                result.organizations.add(*orgs)
                if session['id'] == DZ:
                    if 'redna seja' in session['name'].lower():
                        # call method for create new list of members
                        # setListOfMembers(session['start_time'])
                        pass
            else:
                self.stdout.write('Old session %s' % str(session['id']))
                ses = Session.objects.filter(name=session['name'],
                                            gov_id=session['gov_id'],
                                            start_time=session['start_time'],
                                            end_time=session['end_time'],
                                            classification=session['classification'],
                                            id_parladata=session['id'],
                                            in_review=session['in_review'],
                                            organization=orgs[0])
                ses = ses.exclude(organizations=None)
                if not session:
                    # save changes
                    session2 = Session.objects.get(id_parladata=session['id'])
                    session2.name = session['name']
                    session2.gov_id = session['gov_id']
                    session2.start_time = session['start_time']
                    session2.end_time = session['end_time']
                    session2.classification = session['classification']
                    session2.in_review = session['in_review']
                    session2.organization = orgs[0]
                    session2.save()
                    orgs = list(orgs)
                    session2.organizations.add(*orgs)

        return 0
