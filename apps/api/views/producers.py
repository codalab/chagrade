# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.viewsets import ModelViewSet
# from rest_framework.permissions import IsAdminUser

# from apps.api.serializers import competitions as serializers
# from producers.models import Producer


# class ProducerViewSet(ModelViewSet):
#     queryset = Producer.objects.all()
#     serializer_class = serializers.ProducerSerializer
#     permission_classes = (IsAdminUser,)
#
#     def create(self, request, *args, **kwargs):
#         # Augment the default behavior to return the secret key instead of the entire producer object
#
#         # We then display the API key to the user to forward on to the producer
#
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#
#         return Response({"api_key": serializer.instance.api_key}, status=status.HTTP_201_CREATED, headers=headers)
