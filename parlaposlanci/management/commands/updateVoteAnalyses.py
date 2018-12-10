from django.core.management.base import BaseCommand, CommandError
from parlaposlanci.models import Person, VocabularySize, VocabularySizeUniqueWords, SpokenWords
from parlalize.utils_ import saveOrAbortNew
from utils.speech import WordAnalysis


class Command(BaseCommand):
    help = 'Updates votes analyses static data'

    def handle(self, *args, **options):
        date_of = datetime.now().date()
        date_ = date_of.strftime(API_DATE_FORMAT)
        sw = WordAnalysis(count_of='members', date_=date_)

        #if not sw.isNewSpeech:
        #    return JsonResponse({'alliswell': False})

        #Vocabolary size
        all_score = sw.getVocabularySize()
        max_score, maxMPid = sw.getMaxVocabularySize()
        avg_score = sw.getAvgVocabularySize()
        date_of = sw.getDate()
        maxMP = Person.objects.get(id_parladata=maxMPid)

        commander.stdout.write('[INFO] saving vocabulary size')
        for p in all_score:
            saveOrAbortNew(model=VocabularySize,
                           person=Person.objects.get(id_parladata=int(p['counter_id'])),
                           created_for=date_of,
                           score=int(p['coef']),
                           maxMP=maxMP,
                           average=avg_score,
                           maximum=max_score)

        #Unique words
        all_score = sw.getUniqueWords()
        max_score, maxMPid = sw.getMaxUniqueWords()
        avg_score = sw.getAvgUniqueWords()
        date_of = sw.getDate()
        maxMP = Person.objects.get(id_parladata=maxMPid)

        commander.stdout.write('[INFO] saving unique words')
        for p in all_score:
            saveOrAbortNew(model=VocabularySizeUniqueWords,
                           person=Person.objects.get(id_parladata=int(p['counter_id'])),
                           created_for=date_of,
                           score=int(p['unique']),
                           maxMP=maxMP,
                           average=avg_score,
                           maximum=max_score)

        #Spoken words
        all_words = sw.getSpokenWords()
        max_words, maxWordsMPid = sw.getMaxSpokenWords()
        avgSpokenWords = sw.getAvgSpokenWords()
        date_of = sw.getDate()
        maxMP = Person.objects.get(id_parladata=maxWordsMPid)

        commander.stdout.write('[INFO] saving spoken words')
        for p in all_words:
            saveOrAbortNew(model=SpokenWords,
                           created_for=date_of,
                           person=Person.objects.get(id_parladata=int(p['counter_id'])),
                           score=int(p['wordcount']),
                           maxMP=maxMP,
                           average=avgSpokenWords,
                           maximum=max_words)

        commander.stdout.write('All MPs updated')

        return 0
