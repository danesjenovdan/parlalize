from django.core.management.base import BaseCommand, CommandError
from parlalize.utils_ import tryHard
from parlaposlanci.models import Person, PresenceThroughTime
from parlalize.utils_ import saveOrAbortNew
from datetime import datetime
from parlalize.settings import API_URL, API_DATE_FORMAT, YES, NOT_PRESENT, AGAINST, ABSTAIN


def setPresenceThroughTime(commander, person_id, date_=None):
    if date_:
        fdate = datetime.strptime(date_, '%d.%m.%Y').date()
    else:
        fdate = datetime.now().date()

    url = API_URL + '/getBallotsCounterOfPerson/' + person_id + '/' + fdate.strftime(API_DATE_FORMAT)
    commander.stdout.write('Trying hard with %s' % str(url))
    data = tryHard(url).json()

    data_for_save = []

    commander.stdout.write('Iterating through months for person %s' % str(person_id))
    for month in data:
        options = YES + NOT_PRESENT + AGAINST + ABSTAIN
        stats = sum([month[option] for option in options if option in month.keys()])
        not_member = month['total'] - stats
        not_member = float(not_member) / month['total'] if not_member else 0
        presence = float(stats-sum([month[option] for option in NOT_PRESENT  if option in month.keys()])) / month['total'] if stats else 0
        data_for_save.append({'date_ts': month['date_ts'],
                              'presence': presence * 100,
                              'not_member': not_member * 100,
                              'vote_count': month['total']})

    saveOrAbortNew(model=PresenceThroughTime,
                   person=Person.objects.get(id_parladata=person_id),
                   created_for=fdate,
                   data=data_for_save)

    commander.stdout.write('Set PresenceThroughTime for person id %s' % str(person_id))


class Command(BaseCommand):
    help = 'Updates PresenceThroughTime'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            nargs=1,
            help='date',
        )

    def handle(self, *args, **options):
        if options['date']:
            date_of = datetime.strptime(options['date'], API_DATE_FORMAT).date()
            date_ = options['date']
        else:
            # dirty work around, TODO: fix findDatesFromLastCard for input without person_id
            #date_of = findDatesFromLastCard(Presence, '11', datetime.now().strftime(API_DATE_FORMAT))[0]
            date_of = datetime.now().date()
            date_ = date_of.strftime(API_DATE_FORMAT)

        self.stdout.write('Trying hard for %s/getMPs/%s' % (API_URL, str(date_)))
        mps = tryHard(API_URL+'/getMPs/' + date_).json()
        for mp in mps:
            self.stdout.write('Running setPresenceThroughTime on %s' % str(mp['id']))
            setPresenceThroughTime(self, str(mp['id']), date_)

        return 0