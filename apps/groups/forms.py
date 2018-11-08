from django import forms
from django.forms import DateTimeInput, SelectDateWidget

from apps.groups.models import Team


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = [
            # 'klass',
            'name',
            'description',
            'members'
        ]
