from rest_framework import exceptions, authentication

from producers.models import Producer


class ProducerAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_CHAHUB_API_KEY')
        if not api_key:
            return None

        try:
            producer = Producer.objects.get(api_key=api_key)
            return producer, None
        except Producer.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid producer API key')
