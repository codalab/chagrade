from django.shortcuts import render

# Create your views here.
from django.views import View
from django.views.generic import DetailView, TemplateView


class IndexView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['latest_articles'] = Article.objects.all()[:5]
        return context