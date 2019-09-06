import requests
from copy import deepcopy

from rest_framework.decorators import api_view, permission_classes
from rest_framework_csv import renderers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions

from django.db.models import Count, F, Func, OuterRef, Max, Avg, Subquery
from django.http import Http404

from apps.api.serializers.metrics import MetricsSerializer

from apps.profiles.models import StudentMembership, ChaUser, Instructor
from apps.homework.models import Submission, Definition, SubmissionTracker
from apps.klasses.models import Klass
from apps.groups.models import Team


# To render with CSV, Run a list of dictionaries through a serializer with fields identical to the keys of the
# renderer below. Then they'll be rendered into proper columns with labels (values associated with keys) at the
# top row of the CSV document.


class MetricsTimeOfDayAndHWScoreRenderer(renderers.CSVRenderer):
    labels = {
        'name': 'Homework Name',
        'score': 'Homework Score',
        'time': 'Time of Day',
        'count': 'Submission Count',
    }
    header = list(labels.keys())


class AdminMetricsRenderer(renderers.CSVRenderer):
    labels = {
        'students_join_count': 'Students Joined',
        'instructors_join_count': 'Instructors Joined',
        'klasses_created_count': 'Classes Created',
        'submissions_made_count': 'Submissions Made',
        'score_interval_count': 'Scores on Interval',
        'score_interval': 'Score Interval',
        'date': 'Date',
        'students_total': 'Students Total',
        'instructors_total': 'Instructors Total',
        'users_total': 'Users Total',
        'klasses_total': 'Classes Total',
        'submissions_total': 'Submissions Total',
        'ave_students_per_klass': 'Average Number of Students Per Class',
        'ave_definitions_per_klass': 'Average Number of Homework Definitions Per Class',
        'ave_submissions_per_definition': 'Average Number of Submissions Per Homework Definitions',
    }
    header = list(labels.keys())


class MetricsTeamRenderer(renderers.CSVRenderer):
    labels = {
        'name': 'Homework Name',
        'score': 'Homework Score',
        'time': 'Time of Day',
        'cha_username': 'Chagrade Username',
        'submission_count': 'Submission Count',
        'commit_count': 'Github Commit Count',
    }
    header = list(labels.keys())


def list_of_dicts_to_dict_of_lists(l):
    return {k: [d[k] for d in l] for k in l[0]}


def merge_list_of_lists_of_dicts(input_list):
    # Sort list by lengths of the sub-lists from greatest length to shortest length
    sorted_input_list = sorted(input_list, key=lambda i: -len(i))
    output_list = []
    if len(sorted_input_list) > 0:
        output_list = deepcopy(sorted_input_list.pop(0))
    else:
        return []
    while len(sorted_input_list) > 0:
        next_longest_list = sorted_input_list.pop(0)
        for i in range(len(next_longest_list)):
            output_list[i].update(next_longest_list[i])
    return output_list


class InstructorOrSuperuserPermission(permissions.BasePermission):
    message = 'You are not allowed to access this data.'

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        klass_pk = view.kwargs.get('klass_pk')
        student_pk = view.kwargs.get('student_pk')
        team_pk = view.kwargs.get('team_pk')

        print('In Permission')
        print('klass_pk',klass_pk)
        print('student_pk',student_pk)
        print('team_pk',team_pk)

        if klass_pk:
            klass = None
            try:
                klass = Klass.objects.get(pk=klass_pk)
            except Klass.DoesNotExist:
                raise Http404
            if request.user.instructor == klass.instructor:
                return True

        elif student_pk:
            student = None
            try:
                student = StudentMembership.objects.get(pk=student_pk)
            except StudentMembership.DoesNotExist:
                raise Http404
            if request.user.instructor == student.klass.instructor:
                return True

        elif team_pk:
            team = None
            try:
                team = Team.objects.get(pk=team_pk)
            except Team.DoesNotExist:
                raise Http404
            if request.user.instructor == team.klass.instructor:
                return True

        return False


class TimeDistributionMixin:
    # Empty Default values
    time_distribution_model = None
    time_distribution_kwarg_name = None
    time_distribution_filter_name = None

    def time_distribution_query(self, **kwargs):
        kwarg = kwargs.get(self.time_distribution_kwarg_name)
        filter = {
            self.time_distribution_filter_name: kwarg,
        }
        data = self.time_distribution_model.objects.filter(**filter).extra({'time': "EXTRACT(HOUR FROM created)"}).values('time').order_by('time').annotate(count=Count('pk'))
        return data


class TimeSeriesObjectCreationQueryMixin:
    time_series_model = None
    time_series_creation_date_field_name = None

    def time_series_query(self):
        output_fields = {
            'count': Count('pk'),
            'date': F('datefield')
        }
        time_series_data = self.time_series_model.objects.dates(self.time_series_creation_date_field_name, 'day').values(**output_fields)
        return time_series_data


class ScorePerHWMixin:
    score_per_hw_filter_name = None

    def score_per_hw_query(self, filter_object, team_query=False):
        sub_query_filter = {
            self.score_per_hw_filter_name: filter_object,
            'definition': OuterRef('pk'),
        }
        definition_filter = {
            'klass': filter_object.klass
        }
        if team_query:
            definition_filter['team_based'] = True
        data = Definition.objects.filter(**definition_filter).annotate(
            non_normalized_score=Max(Subquery(
                Submission.objects.filter(**sub_query_filter).values('tracked_submissions__stored_score')[:1])
            )
        ).order_by('due_date').annotate(score=((F('non_normalized_score') - F('baseline_score')) / (F('target_score') - F('baseline_score')))).values('name', 'score')
        return data


class KlassScorePerHWMixin:
    def klass_score_per_hw_query(self, **kwargs):
        klass_pk = kwargs.get('klass_pk')
        data = []
        for definition in Definition.objects.filter(klass=klass_pk).values('pk', 'name', 'target_score', 'baseline_score').order_by('due_date'):
            qs = StudentMembership.objects.filter(
                klass=klass_pk
            ).annotate(
                max_score=Max(Subquery(
                    Submission.objects.filter(
                        id__in=OuterRef('submitted_homeworks'),
                        definition=definition.get('pk')
                    ).values('tracked_submissions__stored_score'))
                )
            ).values_list('max_score', flat=True)[:1]

            sum = 0
            for val in qs:
                if val:
                    sum += val

            avg_score = sum / len(qs)
            target_score = definition.get('target_score')
            baseline_score = definition.get('baseline_score')
            scale_adjusted_score = (avg_score - baseline_score) / (target_score - baseline_score)

            data.append({'name': definition.get('name'), 'score': scale_adjusted_score})
        return data

class TeamContributionsMixin:
    def team_contributions(self, team):
        print('team_contributions_mixin')
        team_submissions = team.members.all().annotate(submission_count=Subquery(
            Submission.objects.filter(team=team, creator=OuterRef('pk')).values('creator').values(
                c=Count('*')))).values('submission_count', cha_username=F('user__username'))

        for i in range(len(team_submissions)):
            if not team_submissions[i].get('submission_count'):
                team_submissions[i]['submission_count'] = 0

        if team.leader:
            latest_submission = team.leader.submitted_homeworks.last()
            github_repo_url = latest_submission.github_url.split('/')
            github_repo_url.insert(4, 'repos')
            github_repo_url[2] = 'api.github.com'
            temp = github_repo_url[3]
            github_repo_url[3] = github_repo_url[4]
            github_repo_url[4] = temp
            contributors_url = '/'.join(github_repo_url[0:6]) + '/stats/contributors'
            resp = requests.get(contributors_url, headers={'Authorization': 'token ' + team.leader.user.github_info.access_token})
            contributors = resp.json()

            usernames = list_of_dicts_to_dict_of_lists(team.members.all().values(chagrade_username=F('user__username'), github_username=F('user__github_info__login')))

            contributor_metrics = []
            outsider_commit_count = 0

            for contributor in contributors:
                author = contributor.get('author')
                github_username = author.get('login')
                if github_username in usernames['github_username']:
                    index = usernames['github_username'].index(github_username)
                    chagrade_username = usernames['chagrade_username'][index]
                    contrib = {
                        'cha_username': chagrade_username,
                        'commit_count': contributor.get('total'),
                    }
                    contributor_metrics.append(contrib)
                else:
                    outsider_commit_count += contributor.get('total', 0)

            if outsider_commit_count > 0:
                outsider_contrib = {
                    'cha_username': 'others',
                    'commit_count': outsider_commit_count,
                }
                contributor_metrics.append(outsider_contrib)
            data = {
                'repo_url': latest_submission.github_url,
                'github_contributions': contributor_metrics,
                'chagrade_submissions': team_submissions,
            }
            return data
        else:
            return


@api_view(['GET'])
@permission_classes(())
def chagrade_overall_metrics(request, version):
    data = {
        "users": ChaUser.objects.count(),
        "students": StudentMembership.objects.count(),
        "instructors": Instructor.objects.count(),
        "submissions": Submission.objects.count(),
        "klasses": Klass.objects.count(),
    }
    return Response(data, status=status.HTTP_200_OK)


#################################################
################# Admin Metrics #################
#################################################

class SubmissionMetricsView(APIView, TimeSeriesObjectCreationQueryMixin):
    permission_classes = (InstructorOrSuperuserPermission,)
    time_series_model = Submission
    time_series_creation_date_field_name = 'created'

    def get(self, request, **kwargs):
        sub_sample = Submission.objects.filter(tracked_submissions__stored_score__isnull=False).order_by('?').values(score=(F('tracked_submissions__stored_score') - F('definition__baseline_score')) / (F('definition__target_score') - F('definition__baseline_score')))[:1000]
        sorted_sample = sorted(list(sub_sample), key=lambda k: k['score'])

        # Histogram settings
        minimum = 0
        maximum = 1.2
        delta = maximum - minimum
        bucket_quantity = 12
        bucket_bounds = []

        for i in range(bucket_quantity + 1):
            bucket_bound = round(minimum + (i * delta / bucket_quantity), 1)
            bucket_bounds.append(bucket_bound)

        i = 0
        j = 0
        bucket = 0
        buckets = []
        while j < len(bucket_bounds):
            if i < len(sorted_sample) and sorted_sample[i].get('score') < bucket_bounds[j]:
                if j != 0:
                    bucket += 1
                i += 1
            else:
                if j != 0:
                    buckets.append(bucket)
                    bucket = 0
                j += 1

        submissions = self.time_series_query()
        output_data = {
           'submissions_made': submissions,
        }

        if len(sorted_sample) > 0:
            output_data['submission_scores'] = {
                'values': buckets,
                'labels': bucket_bounds,
            }
        return Response(output_data)


class StudentMetricsView(APIView, TimeSeriesObjectCreationQueryMixin):
    permission_classes = (InstructorOrSuperuserPermission,)
    time_series_model = StudentMembership
    time_series_creation_date_field_name = 'date_enrolled'

    def get(self, request, **kwargs):
        users = self.time_series_query()
        return Response(users)


class InstructorMetricsView(APIView, TimeSeriesObjectCreationQueryMixin):
    permission_classes = (InstructorOrSuperuserPermission,)
    time_series_model = Instructor
    time_series_creation_date_field_name = 'date_promoted'

    def get(self, request, **kwargs):
        instructors = self.time_series_query()
        return Response(instructors)


class KlassMetricsView(APIView, TimeSeriesObjectCreationQueryMixin):
    permission_classes = (InstructorOrSuperuserPermission,)
    time_series_creation_date_field_name = 'created'
    time_series_model = Klass

    def get(self, request, **kwargs):
        klasses = self.time_series_query()

        class Round(Func):
            function = 'ROUND'
            arity = 2

        ave_students_per_klass = Klass.objects.all().annotate(student_count=Count('enrolled_students')).aggregate(ave_students=Round(Avg('student_count'), 2))
        ave_subs_per_definition = Definition.objects.all().annotate(submission_count=Count('submissions')).aggregate(ave_subs=Round(Avg('submission_count'), 2))
        ave_definitions_per_klass = Klass.objects.all().annotate(definition_count=Count('homework_definitions')).aggregate(ave_definitions=Round(Avg('definition_count'), 2))

        data = {
            'klasses_created': klasses,
        }
        data.update(ave_definitions_per_klass)
        data.update(ave_subs_per_definition)
        data.update(ave_students_per_klass)

        return Response(data)

class UserMetricsCSVView(APIView, TimeSeriesObjectCreationQueryMixin):
    permission_classes = (InstructorOrSuperuserPermission,)
    renderer_classes = (AdminMetricsRenderer)

    time_series_model = Instructor
    time_series_creation_date_field_name = 'date_promoted'

    def get(self, request, **kwargs):
        instructors = self.time_series_query()
        self.time_series_model = StudentMembership
        self.time_series_creation_date_field_name = 'date_enrolled'
        students = self.time_series_query()

        users_total = ChaUser.objects.count()
        students_total = StudentMembership.objects.count()
        instructors_total = Instructor.objects.count()

        # Find union of instructors and students based on date


class KlassMetricsCSVView(APIView, TimeSeriesObjectCreationQueryMixin):
    permission_classes = (InstructorOrSuperuserPermission,)
    renderer_classes = (AdminMetricsRenderer)

    time_series_model = Klass
    time_series_creation_date_field_name = 'created'

    def get(self, request, **kwargs):
        klasses = self.time_series_query()

        klasses_total = Klass.objects.count(),
        ave_students_per_klass = Klass.objects.all().annotate(student_count=Count('enrolled_students')).aggregate(ave_students=Round(Avg('student_count'), 2))
        ave_subs_per_definition = Definition.objects.all().annotate(submission_count=Count('submissions')).aggregate(ave_subs=Round(Avg('submission_count'), 2))
        ave_definitions_per_klass = Klass.objects.all().annotate(definition_count=Count('homework_definitions')).aggregate(ave_definitions=Round(Avg('definition_count'), 2))

        # Render


class SubmissionsMetricsCSVView(APIView, TimeSeriesObjectCreationQueryMixin):
    permission_classes = (InstructorOrSuperuserPermission,)
    renderer_classes = (AdminMetricsRenderer)

    time_series_model = Submission
    time_series_creation_date_field_name = 'created'

    def get(self, request, **kwargs):
        submissions = self.time_series_query()
        submissions_total = Submission.objects.count()

        # Render

#################################################
############## Instructor Metrics ###############
#################################################


class StudentSubmissionTimesView(APIView, TimeDistributionMixin):
    permission_classes = (InstructorOrSuperuserPermission,)
    time_distribution_model = Submission
    time_distribution_kwarg_name = 'student_pk'
    time_distribution_filter_name = 'creator'

    def get(self, request, **kwargs):
        data = self.time_distribution_query(**kwargs)
        return Response(data)


class TeamSubmissionTimesView(APIView, TimeDistributionMixin):
    permission_classes = (InstructorOrSuperuserPermission,)
    time_distribution_model = Submission
    time_distribution_kwarg_name = 'team_pk'
    time_distribution_filter_name = 'team'

    def get(self, request, **kwargs):
        data = self.time_distribution_query(**kwargs)
        return Response(data)


class TeamContributionsView(APIView, TeamContributionsMixin):
    permission_classes = (InstructorOrSuperuserPermission,)

    def get(self, request, **kwargs):
        team_pk = kwargs.get('team_pk')
        team = Team.objects.get(pk=team_pk)
        data = self.team_contributions(team)
        if data:
            data['github_contributions'] = list_of_dicts_to_dict_of_lists(data['github_contributions'])
            data['chagrade_submissions'] = list_of_dicts_to_dict_of_lists(data['chagrade_submissions'])
            return Response(data)
        else:
            return Response('No team leader.', status=status.HTTP_404_NOT_FOUND)


class KlassSubmissionTimesView(APIView, TimeDistributionMixin):
    permission_classes = (InstructorOrSuperuserPermission,)
    time_distribution_model = Submission
    time_distribution_kwarg_name = 'klass_pk'
    time_distribution_filter_name = 'klass'

    def get(self, request, **kwargs):
        data = self.time_distribution_query(**kwargs)
        return Response(data)


class StudentScoresView(APIView, ScorePerHWMixin):
    permission_classes = (InstructorOrSuperuserPermission,)
    score_per_hw_filter_name = 'creator'

    def get(self, request, **kwargs):
        student_pk = kwargs.get('student_pk')
        try:
            student = StudentMembership.objects.get(pk=kwargs.get('student_pk'))
        except StudentMembership.DoesNotExist:
            raise Http404

        data = self.score_per_hw_query(student)
        formatted_data = list_of_dicts_to_dict_of_lists(data)
        return Response(formatted_data)


class TeamScoresView(APIView, ScorePerHWMixin):
    permission_classes = (InstructorOrSuperuserPermission,)
    score_per_hw_filter_name = 'team'

    def get(self, request, **kwargs):
        team_pk = kwargs.get('team_pk')
        try:
            team = Team.objects.get(pk=team_pk)
        except Team.DoesNotExist:
            raise Http404

        data = self.score_per_hw_query(team, team_query=True)
        data = list_of_dicts_to_dict_of_lists(data)
        return Response(data)


class KlassScoresView(APIView, KlassScorePerHWMixin):
    permission_classes = (InstructorOrSuperuserPermission,)
    score_per_hw_filter_name = 'team'

    def get(self, request, **kwargs):
        data = self.klass_score_per_hw_query(**kwargs)
        formatted_data = list_of_dicts_to_dict_of_lists(data)
        return Response(formatted_data)


class InstructorKlassCSVView(APIView, TimeDistributionMixin, KlassScorePerHWMixin):
    permission_classes = (InstructorOrSuperuserPermission,)
    renderer_classes = (MetricsTimeOfDayAndHWScoreRenderer,)

    time_distribution_model = Submission
    time_distribution_kwarg_name = 'klass_pk'
    time_distribution_filter_name = 'klass'

    def get(self, request, **kwargs):
        klass_pk = kwargs.get('klass_pk')
        print(request.query_params.get('format'))

        score_data = self.klass_score_per_hw_query(**kwargs)
        time_data = self.time_distribution_query(**kwargs)
        data = merge_list_of_lists_of_dicts([list(time_data), list(score_data)])

        serializer = MetricsSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class InstructorStudentCSVView(APIView, TimeDistributionMixin, ScorePerHWMixin):
    permission_classes = (InstructorOrSuperuserPermission,)
    renderer_classes = (MetricsTimeOfDayAndHWScoreRenderer,)

    time_distribution_model = Submission
    time_distribution_kwarg_name = 'student_pk'
    time_distribution_filter_name = 'creator'
    score_per_hw_filter_name = 'creator'

    def get(self, request, **kwargs):
        student_pk = kwargs.get('student_pk')
        try:
            student = StudentMembership.objects.get(pk=kwargs.get('student_pk'))
        except StudentMembership.DoesNotExist:
            raise Http404

        score_data = self.score_per_hw_query(student)
        time_data = self.time_distribution_query(**kwargs)
        data = merge_list_of_lists_of_dicts([list(time_data), list(score_data)])

        serializer = MetricsSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class InstructorTeamCSVView(APIView, TimeDistributionMixin, ScorePerHWMixin, TeamContributionsMixin):
    permission_classes = (InstructorOrSuperuserPermission,)
    renderer_classes = (MetricsTeamRenderer,)

    time_distribution_model = Submission
    time_distribution_kwarg_name = 'team_pk'
    time_distribution_filter_name = 'team'
    score_per_hw_filter_name = 'team'

    def union_contribution_lists(self, github_list, chagrade_list):
        GL = sorted(github_list, key = lambda i: i['cha_username'])
        CL = sorted(chagrade_list, key = lambda i: i['cha_username'])

        i = 0
        j = 0
        GL_end = False
        CL_end = False
        output_list = []
        while True:

            if GL_end and CL_end:
                break

            elif not GL_end and (CL_end or (GL[i]['cha_username'] < CL[j]['cha_username'])):
                GL[i]['submission_count'] = 0
                output_list.append(GL[i])
                if i < len(GL) - 1:
                    i += 1
                else:
                    GL_end = True

            elif not CL_end and (GL_end or (CL[j]['cha_username'] < GL[i]['cha_username'])):
                CL[j]['commit_count'] = 0
                output_list.append(CL[j])
                if j < len(CL) - 1:
                    j += 1
                else:
                    CL_end = True

            elif GL[i]['cha_username'] == CL[j]['cha_username']:
                GL[i].update(CL[j])
                output_list.append(GL[i])
                if j < len(CL) - 1:
                    j += 1
                else:
                    CL_end = True
                if i < len(GL) - 1:
                    i += 1
                else:
                    GL_end = True

        return output_list

    def get(self, request, **kwargs):
        team_pk = kwargs.get('team_pk')
        try:
            team = Team.objects.get(pk=team_pk)
        except Team.DoesNotExist:
            raise Http404

        score_data = self.score_per_hw_query(team, team_query=True)
        time_data = self.time_distribution_query(**kwargs)
        team_data = self.team_contributions(team)
        merged_team_data = None

        if team_data:
            merged_team_data = self.union_contribution_lists(list(team_data['github_contributions']), list(team_data['chagrade_submissions']))

        data = merge_list_of_lists_of_dicts([list(time_data), list(score_data), list(merged_team_data)])
        serializer = MetricsSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
