from django.contrib import admin

from parlaposlanci.models import CutVotes, AverageNumberOfSpeechesPerSession

# Register your models here.
admin.site.register(CutVotes)
admin.site.register(AverageNumberOfSpeechesPerSession)