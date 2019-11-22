import uuid

from django.core.exceptions import ObjectDoesNotExist

from apps.profiles.models import ChaUser


def get_unique_username(username, email=None):
    try:
        temp_user = ChaUser.objects.get(username=username)
        if temp_user.email == email:
            # If we have an existing user, and our username collides with the existing, return our current.
            return username
        new_username = username + str(uuid.uuid4())[0:4]
        return get_unique_username(new_username)
    except ObjectDoesNotExist:
        return username
