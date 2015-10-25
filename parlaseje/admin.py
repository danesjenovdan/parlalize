from django.contrib import admin
from parlaseje.models import Session, Vote_graph, Vote


# Register your models here.
admin.site.register(Session)
admin.site.register(Vote_graph)
admin.site.register(Vote)