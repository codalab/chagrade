from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

USER_FIELDS = ['username', 'email']

User = get_user_model()


def create_or_find_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}

    fields = dict((name, kwargs.get(name, details.get(name)))
                  for name in backend.setting('USER_FIELDS', USER_FIELDS))
    if not fields:
        return

    try:
        temp_user = User.objects.get(username=fields['username'])
    except ObjectDoesNotExist:
        print("Could not find user to associate in pipeline")
        temp_user = strategy.create_user(**fields)
    return {
        'is_new': True,
        # 'user': strategy.create_user(**fields)
        'user': temp_user
    }