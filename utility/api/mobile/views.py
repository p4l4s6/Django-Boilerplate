from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as dj_filters
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from . import serializers
from .. import filters
from ... import constants
from ...models import GlobalSettings, Page
from ...utils import payment_utils
from coreapp.utils.auth_utils import get_client_info


class InfoAPI(views.APIView):
    permission_classes = [AllowAny, ]

    @extend_schema(
        responses={200: serializers.InfoSerializer}
    )
    def get(self, request):
        global_settings = GlobalSettings.objects.first()
        serializer = serializers.InfoSerializer(global_settings)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PageReadOnlyAPI(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny, ]
    queryset = Page.objects.filter(is_active=True)
    serializer_class = serializers.PageListSerializer
    filter_backends = (dj_filters.DjangoFilterBackend,)
    filterset_fields = ('page_type',)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return serializers.PageDetailsSerializer
        return self.serializer_class

    @extend_schema(
        responses={200: serializers.PageDetailsSerializer}
    )
    @action(detail=True, methods=['get'], url_path='fixed-page')
    def fixed_page(self, request, pk=None):
        page = Page.objects.filter(page_type=pk, is_active=True).first()
        if page:
            serializer = serializers.PageDetailsSerializer(page)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"detail": _("Page not found")}, status=status.HTTP_404_NOT_FOUND)