from .models import *

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (serializers, viewsets, pagination, permissions,
                            mixins, filters, generics)

class TFIDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tfidf
        fields = '__all__'


class TFIDFView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Tfidf.objects.all().order_by('-created_for')
    serializer_class = TFIDFSerializer
    fields = '__all__'
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('session', 'session__id_parladata')
    ordering_fields = ('-created_for',)


class VoteNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ('id', 'note', 'abstractVisible', 'id_parladata', 'session',)


class VoteNoteView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Vote.objects.all()
    serializer_class = VoteNoteSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('id_parladata', 'session__id_parladata')
    ordering_fields = ('-created_for',)