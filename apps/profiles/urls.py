from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('change_password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('reset_user_password/<int:user_pk>/', views.ResetUserPasswordView.as_view(), name='reset_user_password'),
    path('reset_password_by_email/<uuid:reset_key>/', views.ResetUserPasswordByEmailKeyView.as_view(), name='reset_password_by_email'),
    path('remove_user_password_reset_requests/<int:user_pk>/', views.DeletePasswordResetRequestsView.as_view(), name='remove_user_password_reset_requests'),
    path('request_password_reset/<int:sent_message>/', views.RequestResetView.as_view(), name='request_password_reset'),
    path('password_reset_requests/', views.PasswordRequestsOverView.as_view(), name='password_reset_requests'),
    path('instructor_signup/', views.InstructorProfileCreationView.as_view(), name='instructor_signup'),
    path('instructor_overview/', views.InstructorOverView.as_view(), name='instructor_overview'),
    path('student_overview/', views.StudentOverView.as_view(), name='student_overview'),
    path('my_profile/', views.MyProfileView.as_view(), name='my_profile')
]