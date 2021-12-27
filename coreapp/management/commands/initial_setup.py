from django.core.management.base import BaseCommand
from .utils import setup_utils


class Command(BaseCommand):
    help = 'Initial configuration and settings for application'

    def handle(self, *args, **kwargs):
        print('Initial setup for application')
        setup_utils.load_geo_json()
