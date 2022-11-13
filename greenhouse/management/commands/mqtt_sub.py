from django.core.management.base import BaseCommand
from greenhouse.transmission_parser import subscribe


class Command(BaseCommand):
    def add_arguments(self, parser):
        # parser.add_argument('--name', type=int)
        ...

    def handle(self, *args, **options):
        print('Staring mosquitto daemon')
        subscribe()
