import random

from django.core.management.base import BaseCommand

from apps.factory.factories import KlassFactory, DefinitionFactory, StudentMembershipFactory, SubmissionFactory, SubmissionTrackerFactory
from apps.klasses.models import Klass
from apps.profiles.models import ChaUser
from apps.homework.models import Submission


class Command(BaseCommand):
    help = 'Populates a database with a bunch of random data. This is useful for testing environments.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--num_klasses', '-n',
            default=10,
            type=int,
            dest='num_klasses',
            help='Number of klasses generated.',
        )

    def handle(self, *args, **options):
        num_klasses = options.get('num_klasses')
        print('Original Number of Klasses:', Klass.objects.count())
        print('Original Number of Submissions:', Submission.objects.count())
        print('Original Number of Users:', ChaUser.objects.count())

        for i in range(num_klasses):
            klass = KlassFactory()

            student_quantity = random.randint(1, 10)
            definition_quantity = random.randint(1, 10)
            students = []
            for j in range(student_quantity):
                students.append(StudentMembershipFactory(klass=klass))
            for k in range(definition_quantity):
                definition = DefinitionFactory(klass=klass)
                for student in students:
                    submission = SubmissionFactory(definition=definition, creator=student)
                    SubmissionTrackerFactory(submission=submission)

        print('Final Number of Klasses:', Klass.objects.count())
        print('Final Number of Submissions:', Submission.objects.count())
        print('Final Number of Users:', ChaUser.objects.count())
