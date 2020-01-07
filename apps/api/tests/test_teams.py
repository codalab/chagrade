import json
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from apps.groups.models import Team
from apps.klasses.models import Klass
from apps.profiles.models import Instructor, StudentMembership
User = get_user_model()


class TeamsAPIEndpointsTests(TestCase):

    def setUp(self):
        self.main_user = User.objects.create_user(username='user', password='pass', email='test@email.com')
        self.instructor = Instructor.objects.create(university_name='Test')
        self.main_user.instructor = self.instructor
        self.main_user.save()
        self.student_user = User.objects.create_user(username='student_user',password='pass')
        self.klass = Klass.objects.create(instructor=self.instructor, course_number="1")
        self.student = StudentMembership.objects.create(user=self.student_user, klass=self.klass, student_id='test_id')
        self.team = Team.objects.create(klass=self.klass, name='test', description='test')

    def test_anonymous_user_cannot_perform_crud_teams(self):

        resp = self.client.get(reverse('api:team-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 401

        resp = self.client.post(
            reverse('api:team-list', kwargs={'version': 'v1'}),
            data={
                "klass": '',
                "name": "",
                "description": "",
                "members": ''
            }
        )
        assert resp.status_code == 401

        resp = self.client.put(
            reverse('api:team-detail', kwargs={'version': 'v1', 'pk': 1}),
            data={
                "klass": '',
                "name": "",
                "description": "",
                "members": ''
            },
            content_type='application/json'
        )
        assert resp.status_code == 401

        resp = self.client.delete(reverse('api:team-detail', kwargs={'version': 'v1', 'pk': 1}))
        assert resp.status_code == 401

    def test_student_user_can_only_get_and_post_teams(self):
        self.client.login(username='student_user', password='pass')
        resp = self.client.get(reverse('api:team-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(
            reverse('api:team-list', kwargs={'version': 'v1'}),
            data=json.dumps({
                "klass": self.klass.pk,
                "name": "testteam",
                "members": []
            }),
            content_type='application/json'
        )
        assert resp.status_code == 403

        resp = self.client.patch(
            reverse('api:team-detail',kwargs={'version': 'v1', 'pk': self.team.pk}),
            data=json.dumps({
                "name": 'newtestteam',
                "members": []
            }),
            content_type='application/json'
        )
        assert resp.status_code == 403

        resp = self.client.delete(reverse('api:team-detail', kwargs={'version': 'v1', 'pk': self.team.pk}))
        assert resp.status_code == 403

    def test_instructor_user_can_only_get_and_post_teams(self):
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('api:team-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(
            reverse('api:team-list', kwargs={'version': 'v1'}),
            data=json.dumps({
                "klass": self.klass.pk,
                "name": "testteam",
                'members': []
            }),
            content_type='application/json'
        )
        assert resp.json()['name'] == 'testteam'
        assert resp.status_code == 201

        new_team_pk = resp.json()['id']

        resp = self.client.patch(
            reverse('api:team-detail', kwargs={'version': 'v1', 'pk': new_team_pk}),
            data=json.dumps({
                "name": "newtestteamname",
                "members": []
            }),
            content_type='application/json'
        )
        assert resp.status_code == 200

        resp = self.client.delete(reverse('api:team-detail', kwargs={'version': 'v1', 'pk': new_team_pk}))
        assert resp.status_code == 204

    def test_update_with_empty_members_does_not_delete_student_instance(self):
        initial_student_count = StudentMembership.objects.count()
        self.team.members.add(self.student)

        self.client.login(username='user', password='pass')
        resp = self.client.patch(
            reverse('api:team-detail', kwargs={'version': 'v1', 'pk': self.team.pk}),
            data=json.dumps({
                "klass": self.klass.pk,
                "members": []
            }),
            content_type='application/json'
        )
        assert resp.data['name'] == 'test'
        assert resp.status_code == 200
        assert initial_student_count == StudentMembership.objects.count()
