from urllib.parse import urlparse

from django.conf import settings
from django.core.exceptions import ValidationError


def validate_submission_github_url(value):
    parsed_repo_uri = urlparse(value)
    repo_loc = parsed_repo_uri.netloc
    # If our submission is not from a URL we work with, etc
    if repo_loc not in settings.ALLOWED_SUBMISSION_DOMAINS:
        raise ValidationError(
            message='%(value)s is not a URL from github or a trusted source',
            params={'value': value},
        )
    repo_path = parsed_repo_uri.path
    path_components = repo_path.split('/')
    # If the last component, our file-name, doesn't have a zip extension
    if path_components[-1].split('.')[-1] != 'zip':
        raise ValidationError(
            message='%(value)s does not point to a zip file!',
            params={'value': value},
        )
