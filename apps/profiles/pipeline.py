from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from apps.profiles.models import GithubUserInfo

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


GITHUB_FIELDS = [
    'login',
    'avatar_url',
    'gravatar_id',
    'html_url',
    'name',
    'company',
    'bio',
    'location',
    'created_at',
    'updated_at',
    'node_id',
    'url',
    'followers_url',
    'following_url',
    'gists_url',
    'starred_url',
    'subscriptions_url',
    'organizations_url',
    'repos_url',
    'events_url',
    'received_events_url',
    'access_token',
]


def _create_user_data(user, response, backend_name):
    data = {}
    # --------------------------- Github ----------------------
    if backend_name == 'github':
        data['uid'] = response.get('id')
        for field in GITHUB_FIELDS:
            data[field] = response.get(field)
        if not user.github_info:
            new_github_info = GithubUserInfo.objects.create(**data)
            user.github_info = new_github_info
        else:
            # Only update if they're the same remote id
            if str(user.github_info.uid) == str(data['uid']):
                GithubUserInfo.objects.filter(uid=str(data['uid'])).update(**data)
    user.save()


def user_details(user, **kwargs):
    """Update user details using data from provider."""
    backend = kwargs.get('backend')
    response = kwargs.get('response')

    # If we've been passed a user at this point in the pipeline
    if user:
        _create_user_data(user=user, response=response, backend_name=backend.name)
