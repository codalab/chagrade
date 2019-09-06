from rest_framework import serializers


class MetricsSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=False)
    score = serializers.FloatField(required=False)
    time = serializers.FloatField(required=False)
    count = serializers.IntegerField(required=False)
    cha_username = serializers.CharField(max_length=100, required=False)
    submission_count = serializers.IntegerField(required=False)
    commit_count = serializers.IntegerField(required=False)


