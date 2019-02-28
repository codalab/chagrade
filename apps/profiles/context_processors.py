from apps.profiles.models import PasswordResetRequest


def password_reset_requests_processor(request):
    requests = PasswordResetRequest.objects.all()
    return {'password_reset_requests': requests}
