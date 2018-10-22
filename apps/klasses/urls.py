from django.urls import path

from . import views

app_name = 'klasses'

urlpatterns = [
    path('create/', views.KlassCreationView.as_view(), name='create_klass'),
    path('edit/<int:klass_pk>', views.KlassEditView.as_view(), name='edit_klass'),
    path('wizard/<int:klass_pk>', views.KlassOverView.as_view(), name='klass_details'),
    path('wizard/<int:klass_pk>/enroll', views.KlassEnrollmentView.as_view(), name='klass_enrollment'),
    path('wizard/<int:klass_pk>/define_homework', views.KlassDefineHomeworkView.as_view(), name='klass_homework'),
    path('wizard/<int:klass_pk>/grade_homework', views.KlassGradeHomeworkView.as_view(), name='klass_grading'),
    path('wizard/<int:klass_pk>/activate', views.KlassActivateView.as_view(), name='klass_activate')
]
