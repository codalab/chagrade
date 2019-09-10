from rest_framework import serializers


class InstructorMetricsSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=False)
    score = serializers.FloatField(required=False)
    time = serializers.FloatField(required=False)
    count = serializers.IntegerField(required=False)
    cha_username = serializers.CharField(max_length=100, required=False)
    submission_count = serializers.IntegerField(required=False)
    commit_count = serializers.IntegerField(required=False)


class AdminMetricsSerializer(serializers.Serializer):
    students_join_count = serializers.IntegerField(required=False)
    instructors_join_count = serializers.IntegerField(required=False)
    klasses_created_count = serializers.IntegerField(required=False)
    submissions_made_count = serializers.IntegerField(required=False)
    score_interval_count = serializers.IntegerField(required=False)
    score_interval = serializers.CharField(max_length=100, required=False)
    date = serializers.DateField(required=False)
    students_total = serializers.IntegerField(required=False)
    instructors_total = serializers.IntegerField(required=False)
    users_total = serializers.IntegerField(required=False)
    klasses_total = serializers.IntegerField(required=False)
    submissions_total = serializers.IntegerField(required=False)
    ave_students_per_klass = serializers.FloatField(required=False)
    ave_definitions_per_klass = serializers.FloatField(required=False)
    ave_submissions_per_definition = serializers.FloatField(required=False)

