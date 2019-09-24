from django.urls import reverse
from rest_framework.test import APITestCase

from apps.factory.factories import UserFactory, SubmissionTrackerFactory

from apps.profiles.models import StudentMembership, Instructor, ChaUser
from apps.homework.models import Submission
from apps.klasses.models import Klass


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

    def test_overall_metrics_returns_correct_object_count_totals(self):
        resp = self.client.get(reverse('api:chagrade_overall_metrics', kwargs={'version': 'v1'}))
        data = resp.json()

        assert data['users'] == 22
        assert data['students'] == 10
        assert data['instructors'] == 10
        assert data['klasses'] == 10
        assert data['submissions'] == 10

    # Admin Metrics

    def test_student_time_series_query_returns_correct_total_number_of_objects(self):
        self.client.login(username='admin', password='test')
        resp = self.client.get(reverse('api:chagrade_student_metrics', kwargs={'version': 'v1'}))
        data = resp.json()

        total = 0
        for date in data:
            total += date['count']

        assert StudentMembership.objects.count() == total

    def test_submission_time_series_query_returns_correct_total_number_of_objects(self):
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

    def test_klass_time_series_query_returns_correct_total_number_of_objects(self):
        self.client.login(username='admin', password='test')
        resp = self.client.get(reverse('api:chagrade_klass_metrics', kwargs={'version': 'v1'}))
        data = resp.json()

        klasses = data['klasses_created']
        ave_submissions_per_klass = data['ave_subs']
        ave_definitions_per_klass = data['ave_definitions']
        ave_students_per_klass = data['ave_students']

        total = 0
        for date in klasses:
            total += date['count']

        assert Klass.objects.count() == total
        assert ave_definitions_per_klass == 1.0
        assert ave_submissions_per_klass == 1.0
        assert ave_students_per_klass == 1.0

    def test_instructor_time_series_query_returns_correct_total_number_of_objects(self):
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

        klass = Klass.objects.first()
        resp = self.client.get(reverse('api:klass_submission_times', kwargs={'version': 'v1', 'klass_pk': klass.pk}))
        assert resp.status_code == 401
        resp = self.client.get(reverse('api:klass_scores', kwargs={'version': 'v1', 'klass_pk': klass.pk}))
        assert resp.status_code == 401

    # Do Team Views Permissions
