from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, mixins, views, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django_filters import rest_framework as dj_filters
from . import serializers
from .. import filters
from ...models import GlobalSettings, Page


class GlobalSettingsAPI(views.APIView):
    permission_classes = [IsAdminUser, ]

    @extend_schema(
        responses={200: serializers.GlobalSettingsSerializer}
    )
    def get(self, request):
        global_settings = GlobalSettings.objects.first()
        serializer = serializers.GlobalSettingsSerializer(global_settings)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        responses={200: serializers.GlobalSettingsSerializer}
    )
    def post(self, request):
        global_settings = GlobalSettings.objects.first()
        serializer = serializers.GlobalSettingsSerializer(data=request.data, instance=global_settings)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class PageAdminAPI(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser, ]
    queryset = Page.objects.all()
    serializer_class = serializers.PageSerializer
