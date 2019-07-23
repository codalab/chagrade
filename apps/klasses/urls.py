from django.urls import path

from apps.klasses import views

app_name = 'klasses'

urlpatterns = [
    path('create/', views.CreationView.as_view(), name='create_klass'),
    path('edit/<int:klass_pk>', views.EditView.as_view(), name='edit_klass'),
    path('wizard/<int:klass_pk>', views.OverView.as_view(), name='klass_details'),
    path('wizard/<int:klass_pk>/metrics', views.KlassMetricsView.as_view(), name='klass_metrics'),
    path('wizard/<int:klass_pk>/enroll', views.EnrollmentView.as_view(), name='klass_enrollment'),
    path('wizard/<int:klass_pk>/define_homework', views.DefineHomeworkView.as_view(), name='klass_homework'),
    path('wizard/<int:klass_pk>/grade_homework', views.GradeHomeworkView.as_view(), name='klass_grading'),
    path('wizard/<int:klass_pk>/activate', views.ActivateView.as_view(), name='klass_activate'),
    path('download_student_csv/<int:klass_pk>', views.get_klass_students_as_csv, name='klass_get_student_csv'),
    # path('email_students/<int:klass_pk>/', views.EmailKlassStudentsView.as_view(), name='klass_emaiL_students'),
]
