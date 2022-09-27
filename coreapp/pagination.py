from rest_framework.pagination import LimitOffsetPagination
from django.utils.translation import gettext_lazy as _


class LargeResultsSetPagination(LimitOffsetPagination):
    default_limit = 300
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = None
