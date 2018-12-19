from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer
from drf_writable_nested import WritableNestedModelSerializer

from apps.homework.models import Definition, Criteria, Question, Submission, QuestionAnswer, Grade, CriteriaAnswer
from apps.profiles.models import Instructor, StudentMembership

# from apps.api.serializers.klasses import KlassSerializer


User = get_user_model()


class QuestionAnswerSerializer(ModelSerializer):
    class Meta:
        model = QuestionAnswer
        fields = [
            'question',
            'text',
            'is_correct',
            'id'
        ]


class SubmissionSerializer(WritableNestedModelSerializer):

    question_answers = QuestionAnswerSerializer(many=True, required=False)

    class Meta:
        model = Submission
        fields = [
            'klass',
            'definition',
            'creator',
            'submission_github_url',
            'method_name',
            'method_description',
            'project_url',
            'publication_url',
            'question_answers',
            'id'
        ]


class QuestionSerializer(ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'has_specific_answer',
            'question',
            'answer',
            'id'
        ]


class CriteriaSerializer(ModelSerializer):
    class Meta:
        model = Criteria
        fields = [
            'description',
            'lower_range',
            'upper_range',
            'id'
        ]


# class DefinitionSerializer(ModelSerializer):
class DefinitionSerializer(WritableNestedModelSerializer):
    # instructor = InstructorSerializer()

    criterias = CriteriaSerializer(many=True, required=False)
    custom_questions = QuestionSerializer(many=True, required=False)

    class Meta:
        model = Definition
        fields = (
            'klass',
            'creator',
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
            'criterias',
            'custom_questions',
            'id'
        )


class CriteriaAnswerSerializer(ModelSerializer):
    class Meta:
        model = CriteriaAnswer
        fields = [
            'criteria',
            'score',
            'id'
        ]


class GradeSerializer(WritableNestedModelSerializer):

    criteria_answers = CriteriaAnswerSerializer(many=True, required=False)

    class Meta:
        model = Grade
        fields = [
            'id',
            'submission',
            'evaluator',
            'teacher_comments',
            'instructor_notes',
            'criteria_answers',
            'published'
        ]
