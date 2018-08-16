from .models import *

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (serializers, viewsets, pagination, permissions,
                            mixins, filters, generics)

from django.conf import settings

class TFIDFSerializer(serializers.ModelSerializer):
    #id_parladata = serializers.SerializerMethodField()
    class Meta:
        model = Tfidf
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_for', 'person')

    #def get_id_parladata(self, obj):
    #    return obj.person.id_parladata


class TFIDFView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Tfidf.objects.all().order_by('-created_for')
    serializer_class = TFIDFSerializer
    fields = '__all__'
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('person', 'person__id_parladata')
    ordering_fields = ('-created_for',)
