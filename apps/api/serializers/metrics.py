from rest_framework import serializers


class MetricsSerializer(serializers.Serializer):
    registered_user_count = serializers.IntegerField(required=False)
    competition_count = serializers.IntegerField(required=False)
    competitions_published_count = serializers.IntegerField(required=False)
    submissions_made_count = serializers.IntegerField(required=False)
    users_data_date = serializers.DateField(required=False)
    users_data_count = serializers.IntegerField(required=False)
    competitions_data_date = serializers.DateField(required=False)
    competitions_data_count = serializers.IntegerField(required=False)
    submissions_data_date = serializers.DateField(required=False)
    submissions_data_count = serializers.IntegerField(required=False)


class MetricsTimeOfDayAndHWScoreSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=False)
    score = serializers.FloatField(required=False)
#    time = serializers.CharField(max_length=10, required=False)
    time = serializers.FloatField(required=False)
    count = serializers.IntegerField(required=False)

