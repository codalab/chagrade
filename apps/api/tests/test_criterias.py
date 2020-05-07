from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.homework.models import Definition, Criteria
from apps.klasses.models import Klass
from apps.profiles.models import Instructor

User = get_user_model()


class CriteriaGETMethodTests(TestCase):

    def setUp(self):
        self.main_user = User.objects.create_user(username='user', password='pass', email='test@email.com')
        self.instructor = Instructor.objects.create(university_name='Test')
        self.main_user.instructor = self.instructor
        self.student_user = User.objects.create_user(username='student_user', password='pass')
        self.main_user.save()
        self.klass = Klass.objects.create(instructor=self.instructor, course_number="1")
        self.definition = Definition.objects.create(
            klass=self.klass,
            creator=self.instructor,
            due_date=timezone.now(),
            name='setup',
            description='test'
        )
        self.criteria = Criteria.objects.create(
            definition=self.definition,
            description='Test Criteria',
            lower_range=0,
            upper_range=10,
        )

    def test_anonymous_user_cannot_get_criterias(self):
        resp = self.client.get(reverse('api:criteria-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 401

        resp = self.client.get(reverse('api:criteria-detail', kwargs={'version': 'v1', 'pk': 1}))
        assert resp.status_code == 401

        resp = self.client.post(
            reverse('api:definition-list', kwargs={'version': 'v1'}),
            data={
                'klass': self.klass.pk,
                'due_date': timezone.now(),
                'name': "test",
                'challenge_url': "http://www.test.com/",
                'starting_kit_github_url': "",
                'criterias': [{
                    "description": "string",
                    "lower_range": 0,
                    "upper_range": 10
                }]
            })
        assert resp.status_code == 401

        resp = self.client.put(reverse('api:definition-detail', kwargs={'version': 'v1', 'pk': self.criteria.pk}),
                               data={'klass': self.klass.pk,
                                     'creator': self.instructor.pk,
                                     'name': 'newtestname1'},
                               content_type='application/json')
        assert resp.status_code == 401

        resp = self.client.delete(reverse('api:definition-detail', kwargs={'version': 'v1', 'pk': self.criteria.pk}))
        assert resp.status_code == 401

    def test_student_user_can_only_get_criterias(self):
        self.client.login(username='student_user', password='pass')

        resp = self.client.get(reverse('api:criteria-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.get(reverse('api:criteria-detail', kwargs={'version': 'v1', 'pk': self.criteria.pk}))
        assert resp.json()['description'] == 'Test Criteria'

        resp = self.client.post(
            reverse('api:definition-list', kwargs={'version': 'v1'}),
            data={
                'klass': self.klass.pk,
                'creator': self.instructor.pk,
                'due_date': timezone.now(),
                'name': "test1",
                'challenge_url': "http://www.test.com/",
                'starting_kit_github_url': "",
                'criterias': [{
                    "description": "string",
                    "lower_range": 0,
                    "upper_range": 10
                }]
            })

        assert resp.status_code == 403

        resp = self.client.put(reverse('api:definition-detail', kwargs={'version': 'v1', 'pk': self.criteria.pk}),
                               data={'klass': self.klass.pk,
                                     'creator': self.instructor.pk,
                                     'name': 'newtestname'})
        assert resp.status_code == 403

        resp = self.client.delete(reverse('api:definition-detail', kwargs={'version': 'v1', 'pk': self.criteria.pk}))
        assert resp.status_code == 403

    def test_instructor_user_can_only_get_criterias(self):
        self.client.login(username='user', password='pass')

        resp = self.client.get(reverse('api:criteria-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.get(reverse('api:criteria-detail', kwargs={'version': 'v1', 'pk': self.criteria.pk}))
        assert resp.json()['description'] == 'Test Criteria'

        resp = self.client.post(
            reverse('api:definition-list', kwargs={'version': 'v1'}),
            data={
                'klass': self.klass.pk,
                'creator': self.instructor.pk,
                'due_date': timezone.now(),
                'name': "test",
                'challenge_url': "http://www.test.com/",
                'starting_kit_github_url': "",
                'criterias': [{
                    "description": "string",
                    "lower_range": 0,
                    "upper_range": 10
                }]
            })
        crit_pk = resp.json()['id']
        assert resp.status_code == 201

        resp = self.client.put(reverse('api:definition-detail', kwargs={'version': 'v1', 'pk': crit_pk}),
                               data={'klass': self.klass.pk,
                                     'creator': self.instructor.pk,
                                     'name': 'newtestname1'},
                               content_type='application/json')
        assert resp.status_code == 200

        resp = self.client.delete(reverse('api:definition-detail', kwargs={'version': 'v1', 'pk': crit_pk}))
        assert resp.status_code == 204
