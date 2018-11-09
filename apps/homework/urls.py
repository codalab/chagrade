from django.urls import path

from . import views

app_name = 'homework'

urlpatterns = [
    path('define/<int:klass_pk>/', views.DefinitionFormView.as_view(), name='define_homework'),
    path('edit_definition/<int:klass_pk>/<int:definition_pk>', views.DefinitionEditFormView.as_view(), name='edit_homework_def'),
    path('grade/<int:klass_pk>/submission/<int:submission_pk>/', views.GradeFormView.as_view(), name='grade_homework'),
    path('grade/<int:klass_pk>/submission/<int:submission_pk>/edit/<int:grade_pk>', views.GradeEditFormView.as_view(), name='edit_grade'),
    path('overview/<int:klass_pk>/', views.SubmissionOverView.as_view(), name='overview'),
    path('submit/<int:klass_pk>/<int:definition_pk>/', views.SubmissionFormView.as_view(), name='submit_homework'),
]