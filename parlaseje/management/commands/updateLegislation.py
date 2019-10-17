from django.core.management.base import BaseCommand, CommandError
from parlalize.utils_ import tryHard
from parlaseje.models import Session, Legislation
from parlalize.settings import PARSER_UN, PARSER_PASS, LEGISLATION_STATUS
from datetime import datetime


class Command(BaseCommand):
    help = 'Sets session data'

    def handle(self, *args, **options):
        self.stdout.write('Updating legislation')

        self.stdout.write('Getting data from /law/')
        laws = getLegislationa()
        epas = list(set([law['epa'] for law in laws if law['epa']]))
        self.stdout.write('Iterating through EPAs')
        for epa in set(epas):
            self.stdout.write(str(epa))
            laws = getLegislationa(epa=epa)
            last_obj = None
            sessions = []
            is_ended = False
            print(len(laws), laws)
            for law in laws:
                sessions.append(law['session'])
                law['date'] = datetime.strptime(law['date'], '%Y-%m-%dT%X')
                if not is_ended:
                    if law['procedure_ended']:
                        is_ended = True
                if last_obj:
                    if law['date'] > last_obj['date']:
                        last_obj = law
                else:
                    last_obj = law
            result = Legislation.objects.filter(epa=epa)

            # dont update Legislatin procedure_ended back to False
            if result:
                result = result[0]
                if result.procedure_ended:
                    is_ended = True
                print 'update'
                result.text = last_obj['text']
                result.mdt = last_obj['mdt']
                result.proposer_text = last_obj['proposer_text']
                result.procedure_phase = last_obj['procedure_phase']
                result.procedure = last_obj['procedure']
                result.type_of_law = last_obj['type_of_law']
                result.id_parladata = last_obj['id']
                result.date = last_obj['date']
                result.procedure_ended = is_ended
                result.classification = last_obj['classification']
                result.save()
            else:
                print 'adding'
                result = Legislation(text=last_obj['text'],
                                    epa=last_obj['epa'],
                                    mdt=last_obj['mdt'],
                                    proposer_text=last_obj['proposer_text'],
                                    procedure_phase=last_obj['procedure_phase'],
                                    procedure=last_obj['procedure'],
                                    type_of_law=last_obj['type_of_law'],
                                    id_parladata=last_obj['id'],
                                    date=last_obj['date'],
                                    procedure_ended=is_ended,
                                    classification=last_obj['classification'],
                                    result=LEGISLATION_STATUS[0][0]
                                    )
                result.save()
            sessions = list(set(sessions))
            sessions = list(Session.objects.filter(id_parladata__in=sessions))
            result.sessions.add(*sessions)
        return 0
