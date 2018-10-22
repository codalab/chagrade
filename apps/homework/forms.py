from django import forms
from django.forms import DateTimeInput, SelectDateWidget

from apps.homework.models import HomeworkDefinition, HomeworkSubmission


class HomeworkSubmissionForm(forms.ModelForm):
    class Meta:
        model = HomeworkSubmission
        fields = [
            'submission_github_url'
        ]


class HomeworkDefinitionForm(forms.ModelForm):
    class Meta:
        model = HomeworkDefinition
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
