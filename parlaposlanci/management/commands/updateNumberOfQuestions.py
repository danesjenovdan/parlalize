# TODO needs testing
from django.core.management.base import BaseCommand, CommandError

from parlaposlanci.models import Person, NumberOfQuestions
from parlalize.utils_ import saveOrAbortNew, tryHard, getDataFromPagerApi
from parlalize.settings import API_DATE_FORMAT, API_URL

from datetime import datetime
from collections import Counter


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

        self.stdout.write('Trying hard for %s/getAllQuestions/%s' % (API_URL, str(date_)))
        url = API_URL + '/getAllQuestions/' + date_of.strftime(API_DATE_FORMAT)
        data = getDataFromPagerApi(url)
        self.stdout.write('Trying hard for %s/getMPs/%s' % (API_URL, str(date_)))
        mps = tryHard(API_URL+'/getMPs/'+date_of.strftime(API_DATE_FORMAT)).json()
        mps_ids = [mp['id'] for mp in mps]
        authors = []
        for question in data:
            for author in question['author_id']:
                if author in mps_ids:
                    authors.append(author)

        avg = len(authors)/float(len(mps_ids))
        question_count = Counter(authors)
        max_value = 0
        max_persons = []
        for maxi in question_count.most_common(90):
            if max_value == 0:
                max_value = maxi[1]
            if maxi[1] == max_value:
                max_persons.append(maxi[0])
            else:
                break

        for person_id in mps_ids:
            person = Person.objects.get(id_parladata=person_id)
            saveOrAbortNew(model=NumberOfQuestions,
                           created_for=date_of,
                           person=person,
                           score=question_count[person_id],
                           average=avg,
                           maximum=max_value,
                           maxMPs=max_persons)

            self.stdout.write('Done setting NumberOfQuestions to MP %s' % str(person.id_parladata))

        return 0