from .models import *

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (serializers, viewsets, pagination, permissions,
                            mixins, filters, generics)

from django.conf import settings

class TFIDFSerializer(serializers.ModelSerializer):
    data = serializers.JSONField(help_text='Input is array of TFIDFs words objects.')
    class Meta:
        model = Tfidf
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_for', 'session')


class VoteNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ('id', 'note', 'abstractVisible', 'id_parladata', 'session')
        read_only_fields = ('id', 'id_parladata', 'session')


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ('id', 'id_parladata', 'session')
        read_only_fields = ('id', 'id_parladata', 'session')


class LegislationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Legislation
        fields = ('id', 'note', 'extra_note', 'abstractVisible', 'sessions', 'text', 'epa', 'status', 'result', 'is_exposed', 'icon', 'date', 'has_discussion')
        read_only_fields = ('id', 'sessions', 'epa')


class SessionSerializer(serializers.ModelSerializer):
    votes = serializers.SerializerMethodField()
    speeches = serializers.SerializerMethodField()
    organization = serializers.SerializerMethodField()
    class Meta:
        model = Session
        fields = ('id', 'created_at', 'updated_at', 'name', 'start_time', 'id_parladata', 'start_time', 'gov_id', 'votes', 'speeches', 'organization', 'in_review')

    def get_votes(self, obj):
        return bool(Vote.objects.filter(session=obj))

    def get_speeches(self, obj):
        return bool(Speech.objects.filter(session=obj))

    def get_organization(self, obj):
        return obj.organization.getOrganizationData()


class TFIDFView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Tfidf.objects.all().order_by('-created_for')
    serializer_class = TFIDFSerializer
    fields = '__all__'
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('session', 'session__id_parladata')
    ordering_fields = ('created_for',)


class VoteNoteView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Vote.objects.all()
    serializer_class = VoteNoteSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('id_parladata', 'session__id_parladata')
    ordering_fields = ('created_for',)


class VoteView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    lookup_field = 'id_parladata'


class LegislationView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Legislation.objects.all()
    serializer_class = LegislationSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    ordering_fields = ('date', 'id')
    filter_fields = ('is_exposed', 'status', 'result', 'has_discussion')
    search_fields = ('text', 'epa',)

    def list(self, request, *args, **kwargs):
        response = super(LegislationView, self).list(request, args, kwargs)
        response.data['status_options'] = settings.LEGISLATION_STATUS
        response.data['result_options'] = settings.LEGISLATION_RESULT
        return response

class SessionsView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    ordering_fields = ('start_time', 'id')
