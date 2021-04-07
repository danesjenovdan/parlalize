from django.core.management.base import BaseCommand, CommandError
from parlaskupine.models import Organization, VocabularySize
from django.conf import settings
from parlalize.utils_ import saveOrAbortNew
from utils.parladata_api import getParentOrganizationsWithVoters
from datetime import datetime
from utils.speech import WordAnalysis


class Command(BaseCommand):
    help = 'Update districts.'

    def handle(self, *args, **options):
        date_of = datetime.now().date()
        date_ = date_of.strftime(settings.API_DATE_FORMAT)
        for org_id in getParentOrganizationsWithVoters():
            sw = WordAnalysis(organization_id=org_id, count_of='groups', date_=date_)

            #if not sw.isNewSpeech:
            #    return JsonResponse({'alliswell': True,
            #                         'msg': 'Na ta dan ni bilo govorov'})

            # Vocabolary size
            all_score = sw.getVocabularySize()
            max_score, maxPGid = sw.getMaxVocabularySize()
            avg_score = sw.getAvgVocabularySize()
            date_of = sw.getDate()
            maxPG = Organization.objects.get(id_parladata=maxPGid)

            print('[INFO] saving vocabulary size')
            for p in all_score:
                self.stdout.write('Settings organisation %s' % str(p['counter_id']))
                org = Organization.objects.get(id_parladata=int(p['counter_id']))
                saveOrAbortNew(model=VocabularySize,
                            organization=org,
                            created_for=date_of,
                            score=int(p['coef']),
                            maxOrg=maxPG,
                            average=avg_score,
                            maximum=max_score)

            self.stdout.write('DONE')
        return 0
