from django.urls import path

from . import views

app_name = 'homework'

urlpatterns = [
    path('define/<int:klass_pk>/', views.DefinitionFormView.as_view(), name='define_homework'),
    path('grade/<int:klass_pk>/submission/<int:submission_pk>/', views.GradeFormView.as_view(), name='grade_homework'),
    path('submit/<int:klass_pk>/', views.SubmissionFormView.as_view(), name='submit_homework'),
]