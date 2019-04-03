from django.core.management.base import BaseCommand, CommandError
from parlaposlanci.models import Person, AverageNumberOfSpeechesPerSession
from parlalize.utils_ import saveOrAbortNew, tryHard, getVotersIDs
from datetime import datetime
from parlalize.settings import API_DATE_FORMAT, API_URL


class Command(BaseCommand):
    help = 'Updates AverageNumberOfSpeechesPerSession data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            nargs=1,
            help='PG parladata_ids',
        )

    def handle(self, *args, **options):
        date_ = ''

        if options['date']:
            date_of = datetime.strptime(options['date'], API_DATE_FORMAT).date()
            date_ = options['date']
        else:
            # dirty work around, TODO: fix findDatesFromLastCard for input without person_id
            #date_of = findDatesFromLastCard(Presence, '11', datetime.now().strftime(API_DATE_FORMAT))[0]
            date_of = datetime.now().date()
            date_ = date_of.strftime(API_DATE_FORMAT)

        mps = getVotersIDs()
        mp_scores = []

        for mp in mps:
            self.stdout.write('Handling MP %s' % str(mp))
            self.stdout.write('Trying hard for %s/getSpeechesOfMP/%s/%s' % (API_URL, str(mp), date_))
            mp_no_of_speeches = len(tryHard(API_URL+'/getSpeechesOfMP/' + str(mp)  + (("/"+date_) if date_ else "")).json())

            # fix for "Dajem besedo"
            #mp_no_of_speeches = mp_no_of_speeches - int(tryHard(API_URL + '/getNumberOfFormalSpeeches/' + str(mp) + ("/"+date_) if date_ else "").text)

            self.stdout.write('Trying hard for %s/getNumberOfPersonsSessions/%s/%s' % (API_URL, str(mp), date_))
            mp_no_of_sessions = tryHard(API_URL+ '/getNumberOfPersonsSessions/' + str(mp) + (("/"+date_) if date_ else "")).json()['sessions_with_speech']

            if mp_no_of_sessions > 0:
                mp_scores.append({'id': mp, 'score': mp_no_of_speeches / mp_no_of_sessions})
            else:
                mp_scores.append({'id': mp, 'score': 0})


        mp_scores_sorted = sorted(mp_scores, key=lambda k: k['score'])

        average = sum([mp['score'] for mp in mp_scores])/len(mp_scores)

        for mp in mp_scores_sorted:
            person = Person.objects.get(id_parladata=int(mp['id']))
            score = mp['score']
            self.stdout.write('Saving MP %s' % str(mp))

            saveOrAbortNew(
                model=AverageNumberOfSpeechesPerSession,
                created_for=date_of,
                person=person,
                score=score,
                average=average,
                maximum=mp_scores_sorted[-1]['score'],
                maxMP=Person.objects.get(id_parladata=int(mp_scores_sorted[-1]['id'])))

            self.stdout.write('Done setting AverageNumberOfSpeechesPerSession to MP %s' % str(person.id_parladata))
        return 0
