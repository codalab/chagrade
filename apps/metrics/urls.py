from django.urls import path

from apps.metrics import views

app_name = 'metrics'

urlpatterns = [
    path('klass/<int:klass_pk>', views.KlassMetricsView.as_view(), name='klass'),
    path('admin', views.AdminMetricsView.as_view(), name='admin'),
]
