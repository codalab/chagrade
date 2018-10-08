import datetime
import random
import uuid

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.utils import timezone
from termcolor import colored

from apps.klasses.models import Klass
from apps.profiles.models import ChaUser, StudentMembership, Instructor, AssistantMembership

from faker import Faker

fake = Faker()


class Command(BaseCommand):
    help = 'Creates a specific dummy competition'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            dest='user',
            help='Username of user to use as an instructor',
        )

        parser.add_argument(
            '--university-name',
            type=str,
            dest='university_name',
            help='Name of the university to associate with the instructor',
        )

    def handle(self, *args, **options):
        # Instantiate empty vars
        university_name = None

        if not options.get('user'):
            raise ObjectDoesNotExist("No username for user supplied!")
        else:
            try:
                user = ChaUser.objects.get(username=options['user'])

                if user.instructor:
                    raise Exception("This user already has an instructor!")

                if options.get('university_name'):
                    university_name = options['university_name']
                else:
                    university_name = fake.company()

                user.instructor = Instructor.objects.create(
                    university_name=university_name
                )
            except ObjectDoesNotExist:
                print("Could not find a user with username: '{}' to turn into an instructor!".format(options['user']))
