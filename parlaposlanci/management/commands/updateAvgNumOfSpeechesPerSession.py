from django.core.management.base import BaseCommand, CommandError
from parlaposlanci.models import Person, AverageNumberOfSpeechesPerSession
from parlalize.utils_ import saveOrAbortNew, tryHard
from datetime import datetime
from parlalize.settings import API_DATE_FORMAT, API_URL


class Command(BaseCommand):
    help = 'Updates AverageNumberOfSpeechesPerSession data'

    def handle(self, *args, **options):
        if date_:
            date_of = datetime.strptime(date_, API_DATE_FORMAT).date()
        else:
            # dirty work around, TODO: fix findDatesFromLastCard for input without person_id
            #date_of = findDatesFromLastCard(Presence, '11', datetime.now().strftime(API_DATE_FORMAT))[0]
            date_of = datetime.now().date()
            date_ = ""

        mps = tryHard(API_URL+'/getMPs/'+date_).json()
        mp_scores = []

        for mp in mps:
            print(mp['id'])
            mp_no_of_speeches = len(tryHard(API_URL+'/getSpeechesOfMP/' + str(mp['id'])  + (("/"+date_) if date_ else "")).json())

            # fix for "Dajem besedo"
            #mp_no_of_speeches = mp_no_of_speeches - int(tryHard(API_URL + '/getNumberOfFormalSpeeches/' + str(mp['id']) + ("/"+date_) if date_ else "").text)

            mp_no_of_sessions = tryHard(API_URL+ '/getNumberOfPersonsSessions/' + str(mp['id']) + (("/"+date_) if date_ else "")).json()['sessions_with_speech']

            if mp_no_of_sessions > 0:
                mp_scores.append({'id': mp['id'], 'score': mp_no_of_speeches/mp_no_of_sessions})
            else:
                mp_scores.append({'id': mp['id'], 'score': 0})


        mp_scores_sorted = sorted(mp_scores, key=lambda k: k['score'])

        average = sum([mp['score'] for mp in mp_scores])/len(mp_scores)

        for mp in mp_scores_sorted:
            person = Person.objects.get(id_parladata=int(mp['id']))
            score = mp['score']


            saveOrAbortNew(
                model=AverageNumberOfSpeechesPerSession,
                created_for=date_of,
                person=person,
                score=score,
                average=average,
                maximum=mp_scores_sorted[-1]['score'],
                maxMP=Person.objects.get(id_parladata=int(mp_scores_sorted[-1]['id'])))

            commander.stdout.write('Set AverageNumberOfSpeechesPerSession with id %s' % str(person.id_parladata))
        return 0
