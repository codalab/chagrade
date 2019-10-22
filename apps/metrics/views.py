from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.views.generic import TemplateView
from django.http import Http404
from apps.klasses.models import Klass


class AdminMetricsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'metrics/admin_metrics.html'

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(AdminMetricsView, self).get_context_data(**kwargs)
        context['wiki_page_url'] = 'https://github.com/codalab/chagrade/wiki/Admin-Metrics'
        return context


class KlassMetricsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'metrics/klass_metrics.html'

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        klass_pk = self.kwargs.get('klass_pk')
        try:
            klass = Klass.objects.get(pk=klass_pk)
        except ObjectDoesNotExist:
            raise Http404('Klass object not found')
        if self.request.user.instructor:
            if self.request.user.instructor == klass.instructor:
                return True
        return False

    def get_context_data(self, **kwargs):
        context = super(KlassMetricsView, self).get_context_data(**kwargs)
        context['wiki_page_url'] = 'https://github.com/codalab/chagrade/wiki/Instructor-Metrics'
        klass_pk = self.kwargs['klass_pk']
        try:
            klass = Klass.objects.get(pk=klass_pk)
            context['klass'] = klass
        except ObjectDoesNotExist:
            raise Http404
        return context
