import factory
import factory.fuzzy
import random
import pytz
import uuid


from apps.profiles.models import ChaUser, Instructor, StudentMembership, AssistantMembership, PasswordResetRequest, GithubUserInfo
from apps.homework.models import Definition, Submission, SubmissionTracker, Grade, Question, QuestionAnswer, Criteria, CriteriaAnswer, TeamCustomChallengeURL
from apps.klasses.models import Klass
from apps.groups.models import Group, Team


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChaUser
    username = factory.Faker('user_name')
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    password = 'test'
    date_joined = factory.Faker('date_time_between', start_date='-10y', end_date='now', tzinfo=pytz.UTC)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default ``_create`` with our custom call."""
        manager = cls._get_manager(model_class)
        # The default would use ``manager.create(*args, **kwargs)``
        return manager.create_user(*args, **kwargs)


class InstructorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Instructor
    user = factory.SubFactory(UserFactory)
    university_name = factory.Faker('company')

    @factory.post_generation
    def date_promoted(self, create, extracted, **kwargs):
        if create:
            if extracted:
                self.date_promoted = extracted
            else:
                self.date_promoted = self.user.date_joined
            self.save()


class KlassFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Klass
    instructor = factory.SubFactory(InstructorFactory)
    course_number = factory.Faker('slug')
    active = factory.LazyAttribute(lambda o: random.random() > 0.5)
    @factory.post_generation
    def created(self, create, extracted, **kwargs):
        if create:
            if extracted:
                self.created = extracted
            else:
                self.created = self.instructor.user.date_joined
            self.save()


class StudentMembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StudentMembership
    user = factory.SubFactory(UserFactory)
    klass = factory.SubFactory(KlassFactory)
    student_id = factory.LazyAttribute(lambda o: o.user.username)

    @factory.post_generation
    def date_enrolled(self, create, extracted, **kwargs):
        if create:
            if extracted:
                self.date_enrolled = extracted
            else:
                self.date_enrolled = self.user.date_joined
            self.save()


class AssistantMembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AssistantMembership
    instructor = factory.SubFactory(InstructorFactory)
    klass = factory.SubFactory(KlassFactory)


class PasswordResetRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PasswordResetRequest
    user = factory.SubFactory(UserFactory)


class GithubUserInfoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GithubUserInfo
    uid = factory.Faker('password', length=30, special_chars=False)


class DefinitionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Definition
    klass = factory.SubFactory(KlassFactory)
    name = factory.LazyAttribute(lambda o: 'test homework' + uuid.uuid1().hex)
    due_date = factory.LazyAttribute(lambda o: o.klass.created)
    description = factory.Faker('paragraph')
    team_based = factory.LazyAttribute(lambda o: random.random() > 0.5)
    creator = factory.LazyAttribute(lambda o: o.klass.instructor)


class SubmissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Submission
    definition = factory.SubFactory(DefinitionFactory)
    klass = factory.LazyAttribute(lambda o: o.definition.klass)
    creator = factory.SubFactory(StudentMembershipFactory, klass=factory.SelfAttribute('..klass'))

    @factory.post_generation
    def created(self, create, extracted, **kwargs):
        if create:
            if extracted:
                self.created = extracted
            else:
                self.created = self.creator.date_enrolled
            self.save()


class SubmissionTrackerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SubmissionTracker
    submission = factory.SubFactory(SubmissionFactory)
    stored_status = 'finished'
    stored_score = factory.LazyAttribute(lambda o: random.random() * 1.1)


class GradeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Grade
    submission = factory.SubFactory(SubmissionFactory)
    evaluator = factory.SubFactory(InstructorFactory)
    overall_grade = factory.LazyAttribute(lambda o: int(random.random() * 100))
    published = factory.LazyAttribute(lambda o: random.random() > 0.5)


class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Question
    definition = factory.SubFactory(DefinitionFactory)
    has_specific_answer = False
    question = factory.Faker('sentence')
    answer = factory.Faker('paragraph')


class QuestionAnswerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = QuestionAnswer
    submission = factory.SubFactory(SubmissionFactory)
    question = factory.SubFactory(QuestionFactory)
    text = factory.Faker('text')
    is_correct = factory.LazyAttribute(lambda o: random.random() > 0.5)


class CriteriaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Criteria
    definition = factory.SubFactory(DefinitionFactory)
    description = factory.Faker('sentence')


class CriteriaAnswerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CriteriaAnswer
    grade = factory.SubFactory(GradeFactory)
    criteria = factory.SubFactory(CriteriaFactory)


class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Team
    klass = factory.SubFactory(KlassFactory)


class TeamCustomChallengeURLFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TeamCustomChallengeURL
    team = factory.SubFactory(TeamFactory)
    definition = factory.SubFactory(DefinitionFactory)
    challenge_url = factory.Faker('uri')


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group
    creator = factory.SubFactory(InstructorFactory)
    template = factory.SubFactory(KlassFactory)
    name = factory.Faker('company')
