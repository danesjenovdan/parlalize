from django.core.management.base import BaseCommand, CommandError
from parlaposlanci.models import Person
from parlaskupine.models import Organization
from parlaseje.models import Session, Speech, Debate
from parlalize.settings import API_URL
from utils.parladata_api import getSpeeches

# TODO MAKE ME INTERNATIONAL
def get_the_order(speech_id):
    return speech_id

class Command(BaseCommand):
    help = 'Updates people from Parladata'

    def handle(self, *args, **options):
        existingISs = list(Speech.objects.all().values_list('id_parladata',
                                                            flat=True))
        orgs = {str(org.id_parladata): org.id for org in Organization.objects.all()}
        self.stdout.write('Fetching data from %s/getAllAllSpeeches' % API_URL)
        for page in getSpeeches():
            for dic in page:
                if int(dic['id']) not in existingISs:
                    self.stdout.write('Adding speech %s' % str(dic['id']))
                    person = Person.objects.get(id_parladata=int(dic['speaker']))
                    debate = None
                    if Debate.objects.filter(id_parladata=dic['debate']).count() > 0:
                        debate = Debate.objects.get(id_parladata=dic['debate'])
                    speech = Speech(organization=Organization.objects.get(
                                        id_parladata=int(dic['party'])),
                                    content=dic['content'],
                                    order=dic['order'],
                                    the_order=get_the_order(dic['order']),
                                    agenda_item_order=dic['agenda_item_order'],
                                    session=Session.objects.get(
                                        id_parladata=int(dic['session'])),
                                    start_time=dic['start_time'],
                                    end_time=dic['end_time'],
                                    valid_from=dic['valid_from'],
                                    valid_to=dic['valid_to'],
                                    id_parladata=dic['id'],
                                    debate=debate)
                    speech.save()
                    speech.person.add(person)
                else:
                    self.stdout.write('Updating speech %s' % str(dic['id']))
                    speech = Speech.objects.filter(id_parladata=dic['id'])
                    debate = None
                    if Debate.objects.filter(id_parladata=dic['debate']).count() > 0:
                        debate = Debate.objects.get(id_parladata=dic['debate'])
                    speech.update(valid_from=dic['valid_from'],
                                  valid_to=dic['valid_to'],
                                  agenda_item_order=dic['agenda_item_order'],
                                  organization_id=orgs[str(dic['party'])],
                                  the_order=get_the_order(dic['order']),
                                  debate=debate)

        # delete speeches which was deleted in parladata @dirty fix
        #deleteUnconnectedSpeeches()
        return 0