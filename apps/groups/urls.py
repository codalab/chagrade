from django.urls import path

from . import views

app_name = 'groups'

urlpatterns = [
    path('create/<int:klass_pk>/', views.TeamCreateView.as_view(), name='create_team'),
    path('edit/<int:klass_pk>/<int:team_pk>/', views.TeamEditView.as_view(), name='create_team'),
]
