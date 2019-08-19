from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import TemplateView

from apps.klasses.models import Klass

class AdminMetricsView(LoginRequiredMixin, TemplateView): #UserPassesTestMixin,
    template_name = 'metrics/admin_metrics.html'

    # TODO: Add permissions

    def get_context_data(self, **kwargs):
        context = super(AdminMetricsView, self).get_context_data(**kwargs)
        return context


class KlassMetricsView(LoginRequiredMixin, TemplateView): #UserPassesTestMixin,
    template_name = 'metrics/klass_metrics.html'

    # TODO: Add permissions

    def get_context_data(self, **kwargs):
        context = super(KlassMetricsView, self).get_context_data(**kwargs)
        klass_pk = self.kwargs['klass_pk']
        try:
            klass = Klass.objects.get(pk=klass_pk)
            context['klass'] = klass
        except ObjectDoesNotExist:
            raise Http404
        return context

