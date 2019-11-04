import requests
from copy import deepcopy

from rest_framework.decorators import api_view, permission_classes
from rest_framework_csv import renderers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions

from django.db.models import Count, F, Func, OuterRef, Max, Avg, Subquery
from django.shortcuts import get_object_or_404

from apps.api.serializers.metrics import InstructorMetricsSerializer, AdminMetricsSerializer

from apps.api.permissions import InstructorOrSuperuserPermission

from apps.profiles.models import StudentMembership, ChaUser, Instructor
from apps.homework.models import Submission, Definition
from apps.klasses.models import Klass
from apps.groups.models import Team


# To render with CSV, Run a list of dictionaries through a serializer with fields identical to the keys of the
# renderer below. Then they'll be rendered into proper columns with labels (values associated with keys) at the
# top row of the CSV document.


class KlassRenderer(renderers.CSVRenderer):
    labels = {
        'name': 'Homework Name',
        'score': 'Average Homework Score',
        'time': 'Time of Day',
        'count': 'Submission Count',
    }
    header = list(labels.keys())


class StudentRenderer(renderers.CSVRenderer):
    labels = {
        'name': 'Homework Name',
        'score': 'Homework Score',
        'time': 'Time of Day',
        'count': 'Submission Count',
    }
    header = list(labels.keys())


class AdminMetricsRenderer(renderers.CSVRenderer):
    labels = {
        'date': 'Date',
        'students_join_count': 'Students Joined',
        'instructors_join_count': 'Instructors Joined',
        'klasses_created_count': 'Classes Created',
        'submissions_made_count': 'Submissions Made',
        'students_total': 'Students Total',
        'instructors_total': 'Instructors Total',
        'users_total': 'Users Total',
        'klasses_total': 'Classes Total',
        'submissions_total': 'Submissions Total',
        'ave_students_per_klass': 'Average Number of Students Per Class',
        'ave_definitions_per_klass': 'Average Number of Homework Definitions Per Class',
        'ave_submissions_per_definition': 'Average Number of Submissions Per Homework Definitions',
        'score_interval': 'Score Interval',
        'score_interval_count': 'Scores on Interval',
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


def union_lists(union_key, list1_data, list2_data):
    if not list1_data.get('sorted'):
        l1 = sorted(list1_data['data'], key=lambda i: i[union_key])
    else:
        l1 = list1_data['data']
    if not list2_data.get('sorted'):
        l2 = sorted(list2_data['data'], key=lambda i: i[union_key])
    else:
        l2 = list2_data['data']

    i = 0
    j = 0
    l1_end = False
    l2_end = False
    output_list = []
    while True:

        if l1_end and l2_end:
            break

        elif not l1_end and (l2_end or (l1[i][union_key] < l2[j][union_key])):
            l1[i].update(list2_data.get('unique_pairs'))
            output_list.append(l1[i])
            if i < len(l1) - 1:
                i += 1
            else:
                l1_end = True

        elif not l2_end and (l1_end or (l2[j][union_key] < l1[i][union_key])):
            l2[j].update(list1_data.get('unique_pairs'))
            output_list.append(l2[j])
            if j < len(l2) - 1:
                j += 1
            else:
                l2_end = True

        elif l1[i][union_key] == l2[j][union_key]:
            l1[i].update(l2[j])
            output_list.append(l1[i])
            if j < len(l2) - 1:
                j += 1
            else:
                l2_end = True
            if i < len(l1) - 1:
                i += 1
            else:
                l1_end = True

    return output_list


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


class ScoreDistributionMixin:
    def score_distribution_query(self):
        sub_sample = Submission.objects.filter(tracked_submissions__stored_score__isnull=False).order_by(
            '?').values(score=(F('tracked_submissions__stored_score') - F('definition__baseline_score')) / (
                F('definition__target_score') - F('definition__baseline_score')))[:1000]
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

        data = {
            'values': buckets,
            'labels': bucket_bounds,
        }
        return data


class TimeSeriesObjectCreationQueryMixin:
    time_series_model = None
    time_series_creation_date_field_name = None

    def time_series_query(self, count_field_name='count'):
        output_fields = {
            count_field_name: Count('pk'),
            'date': F('datefield')
        }
        time_series_data = self.time_series_model.objects.dates(self.time_series_creation_date_field_name, 'year').values(**output_fields)
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
        team_submissions = team.members.all().annotate(submission_count=Subquery(
            Submission.objects.filter(team=team, creator=OuterRef('pk')).values('creator').values(
                c=Count('*')))).values('submission_count', cha_username=F('user__username'))

        for i in range(len(team_submissions)):
            if not team_submissions[i].get('submission_count'):
                team_submissions[i]['submission_count'] = 0

        if team.leader:
            if team.leader.user.github_info:
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
                return 'Team leader not connected to Github.'
        else:
            return 'No team leader.'


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


class SubmissionMetricsView(TimeSeriesObjectCreationQueryMixin, ScoreDistributionMixin, APIView):
    permission_classes = (InstructorOrSuperuserPermission,)
    time_series_model = Submission
    time_series_creation_date_field_name = 'created'

    def get(self, request, **kwargs):
        score_distribution = self.score_distribution_query()

        submissions = self.time_series_query()
        output_data = {
            'submissions_made': submissions,
            'submission_scores': score_distribution,
        }
        return Response(output_data)


class StudentMetricsView(TimeSeriesObjectCreationQueryMixin, APIView):
    permission_classes = (InstructorOrSuperuserPermission,)
    time_series_model = StudentMembership
    time_series_creation_date_field_name = 'date_enrolled'

    def get(self, request, **kwargs):
        users = self.time_series_query()
        return Response(users)


class InstructorMetricsView(TimeSeriesObjectCreationQueryMixin, APIView):
    permission_classes = (InstructorOrSuperuserPermission,)
    time_series_model = Instructor
    time_series_creation_date_field_name = 'date_promoted'

    def get(self, request, **kwargs):
        instructors = self.time_series_query()
        return Response(instructors)


class KlassMetricsView(TimeSeriesObjectCreationQueryMixin, APIView):
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


class AdminUserCSVView(TimeSeriesObjectCreationQueryMixin, APIView):
    permission_classes = (InstructorOrSuperuserPermission,)
    renderer_classes = (AdminMetricsRenderer,)

    time_series_model = Instructor
    time_series_creation_date_field_name = 'date_promoted'

    def get(self, request, **kwargs):
        instructors = self.time_series_query(count_field_name='instructors_join_count')
        self.time_series_model = StudentMembership
        self.time_series_creation_date_field_name = 'date_enrolled'
        students = self.time_series_query(count_field_name='students_join_count')

        users_total = ChaUser.objects.count()
        students_total = StudentMembership.objects.count()
        instructors_total = Instructor.objects.count()
        stats = {
            'users_total': users_total,
            'students_total': students_total,
            'instructors_total': instructors_total,
        }

        instructors_data = {
            'data': list(instructors),
            'unique_pairs': {
                'instructors_join_count': 0,
            },
            'sorted': True,
        }

        students_data = {
            'data': list(students),
            'unique_pairs': {
                'students_join_count': 0,
            },
            'sorted': True,
        }

        # Find union of instructors and students based on date
        merged_time_series_data = union_lists('date', instructors_data, students_data)

        if len(merged_time_series_data) > 0:
            merged_time_series_data[0].update(stats)
        else:
            merged_time_series_data.append(stats)

        serializer = AdminMetricsSerializer(data=merged_time_series_data, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class AdminKlassCSVView(TimeSeriesObjectCreationQueryMixin, APIView):
    permission_classes = (InstructorOrSuperuserPermission,)
    renderer_classes = (AdminMetricsRenderer,)

    time_series_model = Klass
    time_series_creation_date_field_name = 'created'

    def get(self, request, **kwargs):
        klasses = self.time_series_query(count_field_name='klasses_created_count')

        class Round(Func):
            function = 'ROUND'
            arity = 2

        klasses_total = Klass.objects.count()
        ave_students_per_klass = Klass.objects.all().annotate(student_count=Count('enrolled_students')).aggregate(ave_students=Round(Avg('student_count'), 2))
        ave_subs_per_definition = Definition.objects.all().annotate(submission_count=Count('submissions')).aggregate(ave_subs=Round(Avg('submission_count'), 2))
        ave_definitions_per_klass = Klass.objects.all().annotate(definition_count=Count('homework_definitions')).aggregate(ave_definitions=Round(Avg('definition_count'), 2))
        data = list(klasses)
        stats = {
            'klasses_total': klasses_total,
            'ave_students_per_klass': ave_students_per_klass.get('ave_students'),
            'ave_definitions_per_klass': ave_definitions_per_klass.get('ave_definitions'),
            'ave_submissions_per_definition': ave_subs_per_definition.get('ave_subs'),
        }
        if len(data) > 0:
            data[0].update(stats)
        else:
            data.append(stats)

        serializer = AdminMetricsSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class AdminSubmissionCSVView(TimeSeriesObjectCreationQueryMixin, ScoreDistributionMixin, APIView):
    permission_classes = (InstructorOrSuperuserPermission,)
    renderer_classes = (AdminMetricsRenderer,)

    time_series_model = Submission
    time_series_creation_date_field_name = 'created'

    def get(self, request, **kwargs):
        submissions = list(self.time_series_query(count_field_name='submissions_made_count'))
        submissions_total = Submission.objects.count()
        stats = {
            'submissions_total': submissions_total,
        }

        score_distribution = self.score_distribution_query()
        label_values = score_distribution.get('labels')
        formatted_data = []
        for i in range(len(score_distribution.get('values'))):
            data = {
                'score_interval': '{:.1f} - {:.1f}'.format(label_values[i], label_values[i + 1]),
                'score_interval_count': score_distribution['values'][i],
            }
            formatted_data.append(data)

        if len(submissions) > 0:
            submissions[0].update(stats)
        else:
            submissions.append(stats)

        data = merge_list_of_lists_of_dicts([formatted_data, submissions])

        serializer = AdminMetricsSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)

#################################################
############## Instructor Metrics ###############
#################################################


class StudentSubmissionTimesView(TimeDistributionMixin, APIView):
    permission_classes = (InstructorOrSuperuserPermission,)
    time_distribution_model = Submission
    time_distribution_kwarg_name = 'student_pk'
    time_distribution_filter_name = 'creator'

    def get(self, request, **kwargs):
        data = self.time_distribution_query(**kwargs)
        return Response(data)


class TeamSubmissionTimesView(TimeDistributionMixin, APIView):
    permission_classes = (InstructorOrSuperuserPermission,)
    time_distribution_model = Submission
    time_distribution_kwarg_name = 'team_pk'
    time_distribution_filter_name = 'team'

    def get(self, request, **kwargs):
        data = self.time_distribution_query(**kwargs)
        return Response(data)


class TeamContributionsView(TeamContributionsMixin, APIView):
    permission_classes = (InstructorOrSuperuserPermission,)

    def get(self, request, **kwargs):
        team_pk = kwargs.get('team_pk')
        team = Team.objects.get(pk=team_pk)
        data = self.team_contributions(team)
        if type(data) == dict:
            data['github_contributions'] = list_of_dicts_to_dict_of_lists(data['github_contributions'])
            data['chagrade_submissions'] = list_of_dicts_to_dict_of_lists(data['chagrade_submissions'])
            return Response(data)
        else:
            return Response(data, status=status.HTTP_404_NOT_FOUND)


class KlassSubmissionTimesView(TimeDistributionMixin, APIView):
    permission_classes = (InstructorOrSuperuserPermission,)
    time_distribution_model = Submission
    time_distribution_kwarg_name = 'klass_pk'
    time_distribution_filter_name = 'klass'

    def get(self, request, **kwargs):
        data = self.time_distribution_query(**kwargs)
        return Response(data)


class StudentScoresView(ScorePerHWMixin, APIView):
    permission_classes = (InstructorOrSuperuserPermission,)
    score_per_hw_filter_name = 'creator'

    def get(self, request, **kwargs):
        student = get_object_or_404(StudentMembership, pk=kwargs.get('student_pk'))
        data = self.score_per_hw_query(student)
        formatted_data = list_of_dicts_to_dict_of_lists(data)
        return Response(formatted_data)


class TeamScoresView(ScorePerHWMixin, APIView):
    permission_classes = (InstructorOrSuperuserPermission,)
    score_per_hw_filter_name = 'team'

    def get(self, request, **kwargs):
        team = get_object_or_404(Team, pk=kwargs.get('team_pk'))
        data = self.score_per_hw_query(team, team_query=True)
        data = list_of_dicts_to_dict_of_lists(data)
        return Response(data)


class KlassScoresView(KlassScorePerHWMixin, APIView):
    permission_classes = (InstructorOrSuperuserPermission,)
    score_per_hw_filter_name = 'team'

    def get(self, request, **kwargs):
        data = self.klass_score_per_hw_query(**kwargs)
        formatted_data = list_of_dicts_to_dict_of_lists(data)
        return Response(formatted_data)


class InstructorKlassCSVView(TimeDistributionMixin, KlassScorePerHWMixin, APIView):
    permission_classes = (InstructorOrSuperuserPermission,)
    renderer_classes = (KlassRenderer,)

    time_distribution_model = Submission
    time_distribution_kwarg_name = 'klass_pk'
    time_distribution_filter_name = 'klass'

    def get(self, request, **kwargs):
        score_data = self.klass_score_per_hw_query(**kwargs)
        time_data = self.time_distribution_query(**kwargs)
        data = merge_list_of_lists_of_dicts([list(time_data), list(score_data)])

        serializer = InstructorMetricsSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class InstructorStudentCSVView(TimeDistributionMixin, ScorePerHWMixin, APIView):
    permission_classes = (InstructorOrSuperuserPermission,)
    renderer_classes = (StudentRenderer,)

    time_distribution_model = Submission
    time_distribution_kwarg_name = 'student_pk'
    time_distribution_filter_name = 'creator'
    score_per_hw_filter_name = 'creator'

    def get(self, request, **kwargs):
        student = get_object_or_404(StudentMembership, pk=kwargs.get('student_pk'))

        score_data = self.score_per_hw_query(student)
        time_data = self.time_distribution_query(**kwargs)
        data = merge_list_of_lists_of_dicts([list(time_data), list(score_data)])

        serializer = InstructorMetricsSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class InstructorTeamCSVView(TimeDistributionMixin, ScorePerHWMixin, TeamContributionsMixin, APIView):
    permission_classes = (InstructorOrSuperuserPermission,)
    renderer_classes = (MetricsTeamRenderer,)

    time_distribution_model = Submission
    time_distribution_kwarg_name = 'team_pk'
    time_distribution_filter_name = 'team'
    score_per_hw_filter_name = 'team'

    def get(self, request, **kwargs):
        team = get_object_or_404(Team, pk=kwargs.get('team_pk'))

        score_data = self.score_per_hw_query(team, team_query=True)
        time_data = self.time_distribution_query(**kwargs)
        team_data = self.team_contributions(team)
        merged_team_data = []

        if type(team_data) == dict:
            gc = team_data.get('github_contributions')
            cs = team_data.get('chagrade_submissions')
        else:
            gc = []
            cs = []

        data1_for_union = {
            'data': gc,
            'unique_pairs': {
                'commit_count': 0,
            },
            'sorted': False,
        }

        data2_for_union = {
            'data': cs,
            'unique_pairs': {
                'submission_count': 0,
            },
            'sorted': False,
        }

        if type(team_data) == dict:
            merged_team_data = union_lists('cha_username', data1_for_union, data2_for_union)

        data = merge_list_of_lists_of_dicts([list(time_data), list(score_data), list(merged_team_data)])
        serializer = InstructorMetricsSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
