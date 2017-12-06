from django.contrib import admin
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from parlaskupine.models import *
from dal import autocomplete
# Register your models here.

class WBAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Organization.objects.none()

        qs = Organization.objects.all()

        if self.q:
            qs = qs.filter(organization__name__icontains=self.q)

        return qs

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
admin.site.register(Tfidf)
