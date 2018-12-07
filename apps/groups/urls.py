from django.urls import path

from . import views

app_name = 'groups'

urlpatterns = [
    path('create/<int:klass_pk>/', views.TeamCreateView.as_view(), name='create_team'),
]
