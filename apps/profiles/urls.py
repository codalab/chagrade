from django.urls import path

from . import views

urlpatterns = [
    path('index/', views.IndexView.as_view(), name='main-view')
]