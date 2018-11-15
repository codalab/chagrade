from django import forms

from apps.klasses.models import Klass


class KlassForm(forms.ModelForm):
    class Meta:
        model = Klass
        fields = [
            # 'instructor',
            # 'students',
            # 'teacher_assistants',
            'title',
            'course_number',
            'description',
            # 'created',
            # 'modified',
            # 'group',
            'image',
            'syllabus',
        ]
