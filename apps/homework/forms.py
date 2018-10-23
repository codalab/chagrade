from django import forms
from django.forms import DateTimeInput, SelectDateWidget

from apps.homework.models import Definition, Submission, Grade


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = [
            'submission_github_url'
        ]


class DefinitionForm(forms.ModelForm):
    class Meta:
        model = Definition
        fields = [
            'due_date',
            'name',
            'description',
            'challenge_url',
            'starting_kit_github_url',
            'ask_method_name',
            'ask_method_description',
            'ask_project_url',
            'ask_publication_url',
            'team_based',
        ]
        widgets = {
            'due_date': SelectDateWidget()
        }


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = [
            'score'
        ]
