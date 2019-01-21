from django.urls import path

from django.contrib.auth import views as auth_views

from . import views

app_name = 'profiles'

urlpatterns = [
    path('logout/', views.logout_view, name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='profiles/login.html'), name='login'),
    # path('change_password/', views.ChangePasswordView.as_view(), name='change_password'),
    # path('set_password/', views.SetPasswordView.as_view(), name='set_password'),
    path('instructor_signup/', views.InstructorProfileCreationView.as_view(), name='instructor_signup'),
    path('instructor_overview/', views.InstructorOverView.as_view(), name='instructor_overview'),
    path('student_overview/', views.StudentOverView.as_view(), name='student_overview'),
    path('my_profile/', views.MyProfileView.as_view(), name='my_profile')
]