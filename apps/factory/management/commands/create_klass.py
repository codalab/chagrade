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
            '--instructor',
            type=str,
            dest='instructor',
            help='Username of user to use as an instructor',
        )

        parser.add_argument(
            '--students',
            type=int,
            dest='students',
            help='Number of students to create',
        )

        parser.add_argument(
            '--assistants',
            type=int,
            dest='assistants',
            help='Number of assistants to create',
        )

        parser.add_argument(
            '--title',
            type=str,
            dest='title',
            help='Title of the course',
        )

        parser.add_argument(
            '--course-number',
            type=str,
            dest='course_number',
            help='Course Number (Slug)',
        )

        parser.add_argument(
            '--description',
            type=str,
            dest='description',
            help='Description of the class',
        )

    def handle(self, *args, **options):
        # Instantiate empty vars
        instructor = None
        students = None
        teacher_assistants = None
        title = None
        course_number = None
        description = None

        # If our options dictionary contains instructor, grab the value and find the user with that username.
        # Else and if that fails, raise an exception
        if options.get('instructor'):
            try:
                user = ChaUser.objects.get(username=options['instructor'])
                if user.instructor:
                    instructor = user.instructor
                else:
                    raise ObjectDoesNotExist(
                        "User with username: '{}' is not an instructor yet!".format(options['instructor']))
            except ObjectDoesNotExist:
                raise ObjectDoesNotExist("Instructor with username: '{}' not found!".format(options['instructor']))
        else:
            raise ObjectDoesNotExist("Instructor username not supplied!")

        if options.get('title'):
            title = options['title']
        else:
            title = fake.catch_phrase()

        if options.get('description'):
            description = options['description']
        else:
            description = fake.sentence(nb_words=13, variable_nb_words=True, ext_word_list=None)

        if options.get('course_number'):
            course_number = options['course_number']
        else:
            raise ObjectDoesNotExist("You must supply a valid course number!")

        try:
            # Create the new class
            new_class = Klass.objects.create(
                instructor=instructor,
                title=title,
                course_number=course_number,
                description=description,
            )

            # Create students if arg was supplied
            if options.get('students'):
                for i in range(options['students']):
                    # Create a user, then create a StudentMembership through User
                    temp_username = "{0}-{1}".format(fake.user_name, random.randint(17, 999))
                    temp_email = "{0}{1}".format(temp_username, "@example.com")

                    new_user = ChaUser.objects.create(
                        username=temp_username,
                        email=temp_email
                    )

                    new_student_member = StudentMembership.objects.create(
                        user=new_user,
                        klass=new_class,
                        student_id=str(uuid.uuid4())[0:20],
                    )

            # Create assistants if the arg was supplied
            if options.get('assistants'):
                for i in range(options['assistants']):
                    # Create a user, then create a StudentMembership through User
                    temp_username = "{0}-{1}".format(fake.user_name, random.randint(17, 999))
                    temp_email = "{0}{1}".format(temp_username, "@example.com")

                    new_user = ChaUser.objects.create(
                        username=temp_username,
                        email=temp_email
                    )

                    new_user.instructor = Instructor.objects.create(
                        university_name=fake.company()
                    )

                    new_assistant_member = AssistantMembership.objects.create(
                        instructor=new_user.instructor,
                        klass=new_class,
                    )
            # Done
        except:
            raise ObjectDoesNotExist("Failed to create competition!")
