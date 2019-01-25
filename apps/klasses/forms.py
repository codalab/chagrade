from django import forms
from apps.klasses.models import Klass


class KlassForm(forms.ModelForm):
    class Meta:
        model = Klass
        fields = [
            'title',
            'course_number',
            'description',
            'image',
            'syllabus',
        ]
