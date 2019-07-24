from django.urls import path
from . import views


app_name = 'homework'

urlpatterns = [
    path('define/<int:klass_pk>/', views.DefinitionFormView.as_view(), name='define_homework'),
    path('edit_definition/<int:klass_pk>/<int:definition_pk>', views.DefinitionEditFormView.as_view(), name='edit_homework_def'),
    path('grade/<int:klass_pk>/submission/<int:submission_pk>/', views.GradeFormView.as_view(), name='grade_homework'),
    path('grade/<int:klass_pk>/submission/<int:submission_pk>/edit/<int:grade_pk>', views.GradeEditFormView.as_view(), name='edit_grade'),
    path('overview/<int:klass_pk>/', views.HomeworkOverView.as_view(), name='overview'),
    path('submissions/<int:definition_pk>/', views.SubmissionListView.as_view(), name='submission_list'),
    path('submission/<int:submission_pk>/', views.SubmissionDetailView.as_view(), name='submission_detail'),
#    path('submission_metrics/<int:definition_pk>/', views.SubmissionMetricsView.as_view(), name='submission_metrics'),
    path('submit/<int:klass_pk>/<int:definition_pk>/', views.SubmissionFormView.as_view(), name='submit_homework'),
    path('submit/<int:klass_pk>/<int:definition_pk>/<int:use_github>/', views.SubmissionFormView.as_view(), name='submit_homework'),
    path('edit_submission/<int:klass_pk>/<int:definition_pk>/<int:submission_pk>/<int:use_github>/', views.SubmissionEditFormView.as_view(), name='edit_submission'),
    path('download_grades_csv/<int:klass_pk>', views.get_klass_grades_as_csv, name='get_grades_csv'),
]