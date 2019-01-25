"""chagrade URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
# from apps.profiles import urls as profile_urls
# from apps.profiles import urls as profile_urls
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    # Our includes
    url(r'^admin/', admin.site.urls),
    url(r'^profiles/', include('apps.profiles.urls', namespace='profiles')),
    url(r'^klasses/', include('apps.klasses.urls', namespace='klasses')),
    url(r'^homework/', include('apps.homework.urls', namespace='homework')),
    url(r'^groups/', include('apps.groups.urls', namespace='groups')),
    url(r'^social/', include('social_django.urls', namespace='social')),
    path('api/<str:version>/', include('apps.api.urls')),
]


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

urlpatterns.append(path('', IndexView.as_view(), name='index'))
