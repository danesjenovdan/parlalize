from django.contrib import admin
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from parlaskupine.models import *
# Register your models here.

admin.site.register(Organization)
admin.site.register(PGStatic)
admin.site.register(PercentOFAttendedSession)
admin.site.register(MPOfPg)
admin.site.register(MostMatchingThem)
admin.site.register(LessMatchingThem)
admin.site.register(DeviationInOrganization)
admin.site.register(CutVotes)
admin.site.register(WorkingBodies)
admin.site.register(VocabularySize)
admin.site.register(StyleScores)
