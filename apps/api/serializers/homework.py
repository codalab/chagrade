from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer
from drf_writable_nested import WritableNestedModelSerializer
from apps.groups.models import Team
from apps.homework.models import Definition, Criteria, Question, Submission, QuestionAnswer, Grade, CriteriaAnswer, \
    TeamCustomChallengeURL

User = get_user_model()


class QuestionAnswerSerializer(ModelSerializer):
    class Meta:
        model = QuestionAnswer
        fields = [
            'question',
            'answer',
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
            'github_url',
            'github_repo_name',
            'github_branch_name',
            'github_commit_hash',
            'method_name',
            'method_description',
            'project_url',
            'publication_url',
            'question_answers',
            'id',
            'team',
            'created',
        ]

        read_only_fields = ['created',]


class QuestionSerializer(ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'type',
            'has_specific_answer',
            'question',
            'candidate_answers',
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


class TeamCustomChallengeURLSerializer(WritableNestedModelSerializer):
    class Meta:
        model = TeamCustomChallengeURL
        fields = [
            # 'definition',
            'team',
            'challenge_url',
            'id'
        ]


class BasicTeamSerializer(ModelSerializer):
    class Meta:
        model = Team
        fields = [
            'name',
            'description',
            'id'
        ]


class DefinitionSerializer(WritableNestedModelSerializer):
    criterias = CriteriaSerializer(many=True, required=False)
    custom_questions = QuestionSerializer(many=True, required=False)
    custom_challenge_urls = TeamCustomChallengeURLSerializer(many=True, required=False)
    teams = BasicTeamSerializer(source='klass.teams', many=True, required=False, default=[], read_only=True)

    class Meta:
        model = Definition
        fields = [
            'klass',
            'creator',
            'due_date',
            'name',
            'description',
            'questions_only',
            'challenge_url',
            'starting_kit_github_url',
            'baseline_score',
            'target_score',
            'ask_method_name',
            'ask_method_description',
            'ask_project_url',
            'ask_publication_url',
            'team_based',
            'criterias',
            'custom_questions',
            'custom_challenge_urls',
            'teams',
            'id'
        ]


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
