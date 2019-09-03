import requests

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions

from django.db.models import Count, F, Func, OuterRef, Max, Avg, Subquery
from django.http import Http404


from apps.profiles.models import StudentMembership, ChaUser, Instructor
from apps.homework.models import Submission, Definition, SubmissionTracker
from apps.klasses.models import Klass
from apps.groups.models import Team


def list_of_dicts_to_dict_of_lists(l):
    return {k: [d[k] for d in l] for k in l[0]}

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
    model = None
    kwarg_name = None
    filter_name = None

    def get(self, request, **kwargs):
        kwarg = kwargs.get(self.kwarg_name)
        filter = {
            self.filter_name: kwarg,
        }
        data = self.model.objects.filter(**filter).extra({'time': "EXTRACT(HOUR FROM created)"}).values('time').order_by('time').annotate(count=Count('pk'))
        return Response(data)


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


class SubmissionMetricsView(APIView):
    permission_classes = (InstructorOrSuperuserPermission,)

    def get(self, request, **kwargs):
        output_fields = {
            'count': Count('pk'),
            'date': F('datefield')
        }

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

        submissions = Submission.objects.dates('created', 'day').values(**output_fields)
        output_data = {
           'submissions_made': submissions,
        }

        if len(sorted_sample) > 0:
            output_data['submission_scores'] = {
                'values': buckets,
                'labels': bucket_bounds,
            }
        return Response(output_data)


class StudentMetricsView(APIView):
    permission_classes = (InstructorOrSuperuserPermission,)

    def get(self, request, **kwargs):
        output_fields = {
            'count': Count('pk'),
            'date': F('datefield')
        }
        users = StudentMembership.objects.dates('date_enrolled', 'day').values(**output_fields)
        return Response(users)


class InstructorMetricsView(APIView):
    permission_classes = (InstructorOrSuperuserPermission,)

    def get(self, request, **kwargs):
        output_fields = {
            'count': Count('pk'),
            'date': F('datefield')
        }
        instructors = Instructor.objects.dates('date_promoted', 'day').values(**output_fields)
        return Response(instructors)


class KlassMetricsView(APIView):
    permission_classes = (InstructorOrSuperuserPermission,)

    def get(self, request, **kwargs):
        output_fields = {
            'count': Count('pk'),
            'date': F('datefield')
        }
        klasses = Klass.objects.dates('created', 'day').values(**output_fields)

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


class StudentSubmissionTimesView(APIView, TimeDistributionMixin):
    permission_classes = (InstructorOrSuperuserPermission,)
    model = Submission
    kwarg_name = 'student_pk'
    filter_name = 'creator'


class TeamSubmissionTimesView(APIView, TimeDistributionMixin):
    permission_classes = (InstructorOrSuperuserPermission,)
    model = Submission
    kwarg_name = 'team_pk'
    filter_name = 'team'


class TeamContributionsView(APIView):
    permission_classes = (InstructorOrSuperuserPermission,)

    def get(self, request, **kwargs):
        team_pk = kwargs.get('team_pk')
        team = Team.objects.get(pk=team_pk)

        team_submissions = Submission.objects.filter(team=team_pk).values('team').values(count=Count('*'))
        team_submissions = team.members.all().annotate(submission_count=Subquery(
            Submission.objects.filter(team=team_pk, creator=OuterRef('pk')).values('creator').values(
                c=Count('*')))).values('submission_count', name=F('user__username'))

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
                        'name': chagrade_username,
                        'commit_count': contributor.get('total'),
                    }
                    contributor_metrics.append(contrib)
                else:
                    outsider_commit_count += contributor.get('total', 0)

            if outsider_commit_count > 0:
                outsider_contrib = {
                    'name': 'others',
                    'commit_count': outsider_commit_count,
                }
                contributor_metrics.append(outsider_contrib)

            data = {
                'repo_url': latest_submission.github_url,
                'github_contributions': list_of_dicts_to_dict_of_lists(contributor_metrics),
                'chagrade_submissions': list_of_dicts_to_dict_of_lists(team_submissions),
            }
            return Response(data)
        else:
            return Response('No team leader.', status=status.HTTP_404_NOT_FOUND)


class KlassSubmissionTimesView(APIView, TimeDistributionMixin):
    permission_classes = (InstructorOrSuperuserPermission,)
    model = Submission
    kwarg_name = 'klass_pk'
    filter_name = 'klass'


class StudentScoresView(APIView):
    permission_classes = (InstructorOrSuperuserPermission,)

    def get(self, request, **kwargs):
        student_pk = kwargs.get('student_pk')
        try:
            student = StudentMembership.objects.get(pk=kwargs.get('student_pk'))
        except StudentMembership.DoesNotExist:
            raise Http404

        data = Definition.objects.filter(klass=student.klass).annotate(
            score=Max(Subquery(
                Submission.objects.filter(
                    creator=student_pk,
                    definition=OuterRef('pk')
                ).values('tracked_submissions__stored_score')[:1])
            )
        ).order_by('due_date').values('name', 'score', 'target_score', 'baseline_score')
        data = list_of_dicts_to_dict_of_lists(data)

        normalized_data = {
            'name': [],
            'score': [],
        }
        for i in range(len(data['name'])):
            normalized_data['name'].append(data['name'][i])
            normalized_score = 0.0
            if data['score'][i] != None:
                target_score = data['target_score'][i]
                baseline_score = data['baseline_score'][i]
                normalized_score = (data['score'][i] - baseline_score) / (target_score - baseline_score)

            normalized_data['score'].append(normalized_score)
        return Response(normalized_data)


class TeamScoresView(APIView):
    permission_classes = (InstructorOrSuperuserPermission,)

    def get(self, request, **kwargs):
        team_pk = kwargs.get('team_pk')
        try:
            team = Team.objects.get(pk=team_pk)
        except Team.DoesNotExist:
            raise Http404

        data = Definition.objects.filter(klass=team.klass, team_based=True).annotate(
            score=Max(Subquery(
                Submission.objects.filter(
                    team=team,
                    definition=OuterRef('pk')
                ).values('tracked_submissions__stored_score')[:1])
            )
        ).order_by('due_date').values('name', 'score', 'target_score', 'baseline_score')
        data = list_of_dicts_to_dict_of_lists(data)

        normalized_data = {
            'name': [],
            'score': [],
        }
        for i in range(len(data['name'])):
            normalized_data['name'].append(data['name'][i])
            normalized_score = 0.0
            if data['score'][i] != None:
                target_score = data['target_score'][i]
                baseline_score = data['baseline_score'][i]
                normalized_score = (data['score'][i] - baseline_score) / (target_score - baseline_score)

            normalized_data['score'].append(normalized_score)
        return Response(normalized_data)


class KlassScoresView(APIView):
    permission_classes = (InstructorOrSuperuserPermission,)

    def get(self, request, **kwargs):

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

            print(qs)
            print(len(qs))
            avg_score = sum(qs) / len(qs)
            target_score = definition.get('target_score')
            baseline_score = definition.get('baseline_score')

            scale_adjusted_score = (avg_score - baseline_score) / (target_score - baseline_score)

            data.append({'name': definition.get('name'), 'score': scale_adjusted_score})
        data = list_of_dicts_to_dict_of_lists(data)
        return Response(data)
