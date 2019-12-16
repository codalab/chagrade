from django.urls import reverse
from django.utils.http import urlencode
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.factory.factories import UserFactory, SubmissionFactory, SubmissionTrackerFactory, DefinitionFactory, KlassFactory, TeamFactory, InstructorFactory

from apps.profiles.models import StudentMembership, Instructor
from apps.homework.models import Submission, Definition
from apps.klasses.models import Klass


User = get_user_model()


class MetricsTests(APITestCase):
    def setUp(self):
        self.user = UserFactory(username='user')
        self.admin = UserFactory(username='admin', is_superuser=True)

        self.submission_trackers = [SubmissionTrackerFactory() for i in range(10)]

        # Average score should be 0.5
        for i in range(10):
            if i < 5:
                self.submission_trackers[i].stored_score = 0.0
            else:
                self.submission_trackers[i].stored_score = 1.0

        self.klass = Klass.objects.first()
        self.team = TeamFactory(klass=self.klass)
        StudentMembership(klass=self.klass)

        random_submission = Submission.objects.first()
        self.team = TeamFactory(klass=random_submission.klass)
        self.student = random_submission.creator
        self.team.members.add(self.student)
        self.team.save()
        definition = random_submission.definition
        definition.team_based = True
        definition.save()

        DefinitionFactory(klass=self.klass)
        self.questions_only_definition = DefinitionFactory(klass=self.klass, questions_only=True)
        submission = SubmissionFactory(creator=self.student, klass=self.klass, definition=self.questions_only_definition)
        SubmissionTrackerFactory(submission=submission)

        submission = SubmissionFactory(creator=self.student, klass=random_submission.klass, definition=random_submission.definition, team=self.team)
        SubmissionTrackerFactory(submission=submission)

    def test_overall_metrics_returns_correct_object_count_totals(self):
        resp = self.client.get(reverse('api:chagrade_overall_metrics', kwargs={'version': 'v1'}))
        data = resp.json()

        assert data['users'] == User.objects.count()
        assert data['students'] == StudentMembership.objects.count()
        assert data['instructors'] == Instructor.objects.count()
        assert data['klasses'] == Klass.objects.count()
        assert data['submissions'] == Submission.objects.count()

    # Admin Metrics

    def test_students_time_series_query_returns_correct_total_number_of_objects(self):
        self.client.login(username='admin', password='test')
        resp = self.client.get(reverse('api:chagrade_student_metrics', kwargs={'version': 'v1'}))
        data = resp.json()

        total = 0
        for date in data:
            total += date['count']

        assert StudentMembership.objects.count() == total

    def test_submissions_time_series_query_and_score_distribution_query_return_correct_total_number_of_objects(self):
        self.client.login(username='admin', password='test')
        resp = self.client.get(reverse('api:chagrade_submission_metrics', kwargs={'version': 'v1'}))
        data = resp.json()
        submissions = data['submissions_made']
        scores = data['submission_scores']

        total = 0
        for date in submissions:
            total += date['count']

        assert Submission.objects.count() == total

        total = 0
        for quantity in scores['values']:
            total += quantity

        assert Submission.objects.count() == total

    def test_klasses_time_series_query_returns_correct_total_number_of_objects(self):
        self.client.login(username='admin', password='test')
        resp = self.client.get(reverse('api:chagrade_klass_metrics', kwargs={'version': 'v1'}))
        data = resp.json()

        klasses = data['klasses_created']
        ave_submissions_per_definition = data['ave_subs']
        ave_definitions_per_klass = data['ave_definitions']
        ave_students_per_klass = data['ave_students']

        total = 0
        for date in klasses:
            total += date['count']

        student_quantity = StudentMembership.objects.count()
        definition_quantity = Definition.objects.count()
        submission_quantity = Submission.objects.count()
        klass_quantity = Klass.objects.count()

        assert Klass.objects.count() == total
        assert ave_definitions_per_klass == definition_quantity / klass_quantity
        assert ave_submissions_per_definition == submission_quantity / definition_quantity
        assert ave_students_per_klass == student_quantity / klass_quantity

    def test_instructors_time_series_query_returns_correct_total_number_of_objects(self):
        self.client.login(username='admin', password='test')
        resp = self.client.get(reverse('api:chagrade_instructor_metrics', kwargs={'version': 'v1'}))
        data = resp.json()

        total = 0
        for date in data:
            total += date['count']

        assert Instructor.objects.count() == total

    def test_non_superusers_cannot_see_admin_views(self):
        self.client.login(username='user', password='test')
        resp = self.client.get(reverse('api:chagrade_student_metrics', kwargs={'version': 'v1'}))
        assert resp.status_code == 403
        resp = self.client.get(reverse('api:chagrade_instructor_metrics', kwargs={'version': 'v1'}))
        assert resp.status_code == 403
        resp = self.client.get(reverse('api:chagrade_klass_metrics', kwargs={'version': 'v1'}))
        assert resp.status_code == 403
        resp = self.client.get(reverse('api:chagrade_submission_metrics', kwargs={'version': 'v1'}))
        assert resp.status_code == 403
        resp = self.client.get(reverse('api:klasses_CSV', kwargs={'version': 'v1'}))
        assert resp.status_code == 403
        resp = self.client.get(reverse('api:users_CSV', kwargs={'version': 'v1'}))
        assert resp.status_code == 403
        resp = self.client.get(reverse('api:submissions_CSV', kwargs={'version': 'v1'}))
        assert resp.status_code == 403

    def test_unauthenticated_users_cannot_see_admin_views(self):
        resp = self.client.get(reverse('api:chagrade_student_metrics', kwargs={'version': 'v1'}))
        assert resp.status_code == 401
        resp = self.client.get(reverse('api:chagrade_instructor_metrics', kwargs={'version': 'v1'}))
        assert resp.status_code == 401
        resp = self.client.get(reverse('api:chagrade_klass_metrics', kwargs={'version': 'v1'}))
        assert resp.status_code == 401
        resp = self.client.get(reverse('api:chagrade_submission_metrics', kwargs={'version': 'v1'}))
        assert resp.status_code == 401
        resp = self.client.get(reverse('api:klasses_CSV', kwargs={'version': 'v1'}))
        assert resp.status_code == 401
        resp = self.client.get(reverse('api:users_CSV', kwargs={'version': 'v1'}))
        assert resp.status_code == 401
        resp = self.client.get(reverse('api:submissions_CSV', kwargs={'version': 'v1'}))
        assert resp.status_code == 401

    # Instructor Metrics

    def test_unauthenticated_users_cannot_see_instructor_views(self):
        student = StudentMembership.objects.first()
        resp = self.client.get(reverse('api:student_submission_times', kwargs={'version': 'v1', 'student_pk': student.pk}))
        assert resp.status_code == 401
        resp = self.client.get(reverse('api:student_scores', kwargs={'version': 'v1', 'student_pk': student.pk}))
        assert resp.status_code == 401
        resp = self.client.get(reverse('api:student_CSV', kwargs={'version': 'v1', 'student_pk': student.pk}))
        assert resp.status_code == 401

        resp = self.client.get(reverse('api:klass_submission_times', kwargs={'version': 'v1', 'klass_pk': self.klass.pk}))
        assert resp.status_code == 401
        resp = self.client.get(reverse('api:klass_scores', kwargs={'version': 'v1', 'klass_pk': self.klass.pk}))
        assert resp.status_code == 401
        resp = self.client.get(reverse('api:klass_CSV', kwargs={'version': 'v1', 'klass_pk': self.klass.pk}))
        assert resp.status_code == 401

        resp = self.client.get(reverse('api:team_submission_times', kwargs={'version': 'v1', 'team_pk': self.team.pk}))
        assert resp.status_code == 401
        resp = self.client.get(reverse('api:team_scores', kwargs={'version': 'v1', 'team_pk': self.team.pk}))
        assert resp.status_code == 401
        resp = self.client.get(reverse('api:team_CSV', kwargs={'version': 'v1', 'team_pk': self.team.pk}))
        assert resp.status_code == 401

    def test_non_instructors_cannot_see_instructor_views(self):
        # Creates new instructor of new klass. The important thing is that this instructor is not an instructor of the
        # klass related to the objects in the queries.
        self.client.login(username=InstructorFactory().user.username, password='test')

        student = self.klass.enrolled_students.first()
        resp = self.client.get(reverse('api:student_submission_times', kwargs={'version': 'v1', 'student_pk': student.pk}))
        assert resp.status_code == 403
        resp = self.client.get(reverse('api:student_scores', kwargs={'version': 'v1', 'student_pk': student.pk}))
        assert resp.status_code == 403
        resp = self.client.get(reverse('api:student_CSV', kwargs={'version': 'v1', 'student_pk': student.pk}))
        assert resp.status_code == 403

        resp = self.client.get(reverse('api:klass_submission_times', kwargs={'version': 'v1', 'klass_pk': self.klass.pk}))
        assert resp.status_code == 403
        resp = self.client.get(reverse('api:klass_scores', kwargs={'version': 'v1', 'klass_pk': self.klass.pk}))
        assert resp.status_code == 403
        resp = self.client.get(reverse('api:klass_CSV', kwargs={'version': 'v1', 'klass_pk': self.klass.pk}))
        assert resp.status_code == 403

        resp = self.client.get(reverse('api:team_submission_times', kwargs={'version': 'v1', 'team_pk': self.team.pk}))
        assert resp.status_code == 403
        resp = self.client.get(reverse('api:team_scores', kwargs={'version': 'v1', 'team_pk': self.team.pk}))
        assert resp.status_code == 403
        resp = self.client.get(reverse('api:team_CSV', kwargs={'version': 'v1', 'team_pk': self.team.pk}))
        assert resp.status_code == 403

    def test_instructor_of_klass_can_see_instructor_views(self):
        # Creates new instructor of new klass. The important thing is that this instructor is not an instructor of the
        # klass related to the objects in the queries.
        self.client.login(username=self.klass.instructor.user.username, password='test')

        student = self.klass.enrolled_students.first()
        resp = self.client.get(reverse('api:student_submission_times', kwargs={'version': 'v1', 'student_pk': student.pk}))
        assert resp.status_code == 200
        resp = self.client.get(reverse('api:student_scores', kwargs={'version': 'v1', 'student_pk': student.pk}))
        assert resp.status_code == 200
        resp = self.client.get(reverse('api:student_CSV', kwargs={'version': 'v1', 'student_pk': student.pk}))
        assert resp.status_code == 200

        resp = self.client.get(reverse('api:klass_submission_times', kwargs={'version': 'v1', 'klass_pk': self.klass.pk}))
        assert resp.status_code == 200
        resp = self.client.get(reverse('api:klass_scores', kwargs={'version': 'v1', 'klass_pk': self.klass.pk}))
        assert resp.status_code == 200
        resp = self.client.get(reverse('api:klass_CSV', kwargs={'version': 'v1', 'klass_pk': self.klass.pk}))
        assert resp.status_code == 200

        resp = self.client.get(reverse('api:team_submission_times', kwargs={'version': 'v1', 'team_pk': self.team.pk}))
        assert resp.status_code == 200
        resp = self.client.get(reverse('api:team_scores', kwargs={'version': 'v1', 'team_pk': self.team.pk}))
        assert resp.status_code == 200
        resp = self.client.get(reverse('api:team_CSV', kwargs={'version': 'v1', 'team_pk': self.team.pk}))
        assert resp.status_code == 200

    def test_student_submission_times_query_return_correct_total_number_of_objects(self):
        self.client.login(username='admin', password='test')
        resp = self.client.get(reverse('api:student_submission_times', kwargs={'version': 'v1', 'student_pk': self.student.pk}))
        times = resp.json()

        total = 0
        for time in times:
            total += time['count']

        assert Submission.objects.filter(creator=self.student.pk).count() == total

        url = reverse('api:student_submission_times', kwargs={'version': 'v1', 'student_pk': self.student.pk})
        query_parameters = urlencode({'questions_only': True})
        resp = self.client.get(f'{url}?{query_parameters}')
        times = resp.json()

        total = 0
        for time in times:
            total += time['count']

        assert Submission.objects.filter(creator=self.student.pk, definition__questions_only=True).count() == total

    def test_student_score_per_hw_query_return_correct_total_number_of_objects(self):
        self.client.login(username='admin', password='test')
        resp = self.client.get(reverse('api:student_scores', kwargs={'version': 'v1', 'student_pk': self.student.pk}))
        scores = resp.json()
        total = len(scores['score'])

        assert self.student.klass.homework_definitions.count() == total

        url = reverse('api:student_scores', kwargs={'version': 'v1', 'student_pk': self.student.pk})
        query_parameters = urlencode({'questions_only': True})
        resp = self.client.get(f'{url}?{query_parameters}')
        scores = resp.json()
        total = len(scores['grade'])

        assert self.student.klass.homework_definitions.filter(questions_only=True).count() == total

    def test_team_submission_times_query_return_correct_total_number_of_objects(self):
        self.client.login(username='admin', password='test')
        resp = self.client.get(reverse('api:team_submission_times', kwargs={'version': 'v1', 'team_pk': self.team.pk}))
        submissions = resp.json()

        total = 0
        for submission in submissions:
            total += submission['count']

        assert Submission.objects.filter(team=self.team.pk).count() == total

        url = reverse('api:team_submission_times', kwargs={'version': 'v1', 'team_pk': self.team.pk})
        query_parameters = urlencode({'questions_only': True})
        resp = self.client.get(f'{url}?{query_parameters}')
        submissions = resp.json()

        total = 0
        for submission in submissions:
            total += submission['count']

        assert Submission.objects.filter(team=self.team.pk, definition__questions_only=True).count() == total

    def test_team_submission_scores_query_return_correct_total_number_of_objects(self):
        self.client.login(username='admin', password='test')
        resp = self.client.get(reverse('api:team_scores', kwargs={'version': 'v1', 'team_pk': self.team.pk}))
        scores = resp.json()
        total = len(scores['score'])

        assert self.team.klass.homework_definitions.filter(team_based=True).count() == total

    def test_team_contributions_returns_404_when_no_team_leader_exists(self):
        self.client.login(username='admin', password='test')
        resp = self.client.get(reverse('api:team_contributions', kwargs={'version': 'v1', 'team_pk': self.team.pk}))
        assert resp.status_code == 404

    def test_team_contributions_returns_404_when_team_leader_is_not_connected_to_github(self):
        self.client.login(username='admin', password='test')
        self.team.leader = self.student
        self.team.save()
        resp = self.client.get(reverse('api:team_contributions', kwargs={'version': 'v1', 'team_pk': self.team.pk}))
        assert resp.status_code == 404

    def test_klass_submission_times_query_return_correct_total_number_of_objects(self):
        self.client.login(username='admin', password='test')
        resp = self.client.get(reverse('api:klass_submission_times', kwargs={'version': 'v1', 'klass_pk': self.klass.pk}))
        submissions = resp.json()

        total = 0
        for submission in submissions:
            total += submission['count']

        assert Submission.objects.filter(klass=self.klass.pk).count() == total

        url = reverse('api:klass_submission_times', kwargs={'version': 'v1', 'klass_pk': self.klass.pk})
        query_parameters = urlencode({'questions_only': True})
        resp = self.client.get(f'{url}?{query_parameters}')
        submissions = resp.json()

        total = 0
        for submission in submissions:
            total += submission['count']

        assert Submission.objects.filter(klass=self.klass.pk, definition__questions_only=True).count() == total

    def test_klass_submission_scores_query_return_correct_total_number_of_objects(self):
        self.client.login(username='admin', password='test')
        resp = self.client.get(reverse('api:klass_scores', kwargs={'version': 'v1', 'klass_pk': self.klass.pk}))
        scores = resp.json()
        total = len(scores['score'])

        assert self.klass.homework_definitions.count() == total

        url = reverse('api:klass_scores', kwargs={'version': 'v1', 'klass_pk': self.klass.pk})
        query_parameters = urlencode({'questions_only': True})
        resp = self.client.get(f'{url}?{query_parameters}')
        scores = resp.json()
        total = len(scores['average_grade'])

        assert self.klass.homework_definitions.filter(questions_only=True).count() == total
