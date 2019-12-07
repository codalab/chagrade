import logging

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.api.permissions import SubmissionPermissionCheck, GradePermissionCheck, DefinitionPermissionCheck, \
    QuestionPermissionCheck, CriteriaPermissionCheck, CustomChallengeURLPermissionCheck
from apps.api.serializers.homework import DefinitionSerializer, QuestionSerializer, CriteriaSerializer, \
    SubmissionSerializer, GradeSerializer, TeamCustomChallengeURLSerializer
from apps.homework.models import Definition, Question, Criteria, Submission, Grade, TeamCustomChallengeURL
from apps.homework.tasks import post_submission, SubmissionPostException

User = get_user_model()

logger = logging.getLogger(__name__)


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

    def create(self, request, *args, **kwargs):
        """Overwritten so we can return responses or default from post_submission"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = self.perform_create(serializer)
        if response:
            return response
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        new_sub = serializer.save()
        if new_sub.pk and not new_sub.submitted_to_challenge:
            file_to_submit = self.request.data.get('file')
            if not new_sub.definition.questions_only and ( new_sub.github_url or file_to_submit ):
                if file_to_submit:
                    logger.info(f"Submission {new_sub.pk} is a direct upload!")
                    new_sub.is_direct_upload = True
                    new_sub.save()
                else:
                    logger.info(f"Submission {new_sub.pk} is a github submission!")
                try:
                    post_submission(new_sub.pk, file_to_submit)
                except SubmissionPostException as e:
                    if e.sub_type == 'connection':
                        return Response("Could not communicate with Codalab instance!", status=status.HTTP_504_GATEWAY_TIMEOUT)
                    else:
                        return Response(
                            "Could not determine data to send to Codalab. Check you supplied a proper github_url, or a "
                            "file for direct upload.",
                            status=status.HTTP_400_BAD_REQUEST
                        )


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
