from apps.profiles.models import PasswordResetRequest


def password_reset_requests_processor(request):
    if request.user.is_staff or request.user.is_superuser:
        requests = PasswordResetRequest.objects.all()
        return {'password_reset_requests': requests}
    return {}
