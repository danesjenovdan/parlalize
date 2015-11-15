from django.contrib import admin

from parlaposlanci.models import CutVotes, AverageNumberOfSpeechesPerSession, VocabularySize

# Register your models here.
admin.site.register(CutVotes)
admin.site.register(AverageNumberOfSpeechesPerSession)
admin.site.register(VocabularySize)