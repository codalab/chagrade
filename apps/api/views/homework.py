from django.contrib.auth import get_user_model
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.views import APIView


from apps.api.permissions import SubmissionPermissionCheck, GradePermissionCheck, DefinitionPermissionCheck, \
    QuestionPermissionCheck, CriteriaPermissionCheck, CustomChallengeURLPermissionCheck
from apps.api.serializers.homework import DefinitionSerializer, QuestionSerializer, CriteriaSerializer, \
    SubmissionSerializer, GradeSerializer, TeamCustomChallengeURLSerializer
from apps.homework.models import Definition, Question, Criteria, Submission, Grade, TeamCustomChallengeURL

from apps.homework.tasks import post_submission

User = get_user_model()


class GradeViewSet(ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = (GradePermissionCheck,)

    def perform_create(self, serializer):
        new_obj = serializer.save()
        new_obj.calculate_grade()

    def perform_update(self, serializer):
        new_obj = serializer.save()
        new_obj.calculate_grade()


class SubmissionViewSet(ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = (SubmissionPermissionCheck,)

    def perform_create(self, serializer):
        new_sub = serializer.save()
        if new_sub.pk and not new_sub.submitted_to_challenge:
            # from apps.homework.tasks import post_submission
            # post_submission.delay(new_sub.pk)
            if not new_sub.definition.questions_only:
                post_submission(new_sub.pk)


class DefinitionViewSet(ModelViewSet):
    queryset = Definition.objects.all()
    serializer_class = DefinitionSerializer
    permission_classes = (DefinitionPermissionCheck,)


class QuestionViewSet(ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = (QuestionPermissionCheck,)


class CriteriaViewSet(ModelViewSet):
    queryset = Criteria.objects.all()
    serializer_class = CriteriaSerializer
    permission_classes = (CriteriaPermissionCheck, )


class CustomChallengeURLViewSet(ModelViewSet):
    queryset = TeamCustomChallengeURL.objects.all()
    serializer_class = TeamCustomChallengeURLSerializer
    permission_classes = (CustomChallengeURLPermissionCheck, )
