from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.klasses.models import Klass
from apps.profiles.models import Instructor
from apps.homework.models import Submission
from apps.profiles.models import ChaUser, StudentMembership


User = get_user_model()


class KlassesIntegrationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass')
        self.instructor = Instructor.objects.create(university_name='Test')
        self.user.instructor = self.instructor
        self.user.save()
        self.klass = Klass.objects.create(instructor=self.instructor, course_number="1")

    def test_edit_klass_changes_object(self):
        self.client.login(username='user', password='pass')

        # This view takes a form to update a Klass object. Fields for the object must be on the form
        resp = self.client.post(
            path=reverse('klasses:edit_klass', kwargs={'klass_pk': self.klass.pk}),
            data={
                'instructor': self.instructor,
                'title': 'Test 123',
                'course_number': 'CSD-TEST',
                'description': 'THIS IS A TEST',
                'pk': self.klass.pk
            }
        )
        assert resp.status_code == 302
        # Refresh our object after we make a POST request
        self.klass.refresh_from_db()
        assert self.klass.title == 'Test 123'
        assert self.klass.course_number == 'CSD-TEST'
        assert self.klass.description == 'THIS IS A TEST'
