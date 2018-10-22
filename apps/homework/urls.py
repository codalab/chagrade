from django.urls import path

from . import views

app_name = 'homework'

urlpatterns = [
    path('define/<int:klass_pk>/', views.DefineHomeworkFormView.as_view(), name='define_homework'),
]