from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import TemplateView

from apps.klasses.models import Klass

class AdminMetricsView(LoginRequiredMixin, TemplateView): #UserPassesTestMixin,
    template_name = 'metrics/admin_metrics.html'

    def get_context_data(self, **kwargs):
        context = super(AdminMetricsView, self).get_context_data(**kwargs)
        return context

#    def test_func(self):
#        definition_pk = self.kwargs.get('definition_pk')
#        try:
#            definition = Definition.objects.get(pk=definition_pk)
#        except ObjectDoesNotExist:
#            raise Http404('Definition object not found')
#        if self.request.user.instructor:
#            if self.request.user.instructor == definition.klass.instructor:
#                print('User is instructor of class.')
#                return True
#        try:
#            if self.request.user.klass_memberships.get(klass__pk=definition.klass.pk):
#                print('User is student of class.')
#                return True
#        except ObjectDoesNotExist:
#            return False
#        return False

class KlassMetricsView(LoginRequiredMixin, TemplateView): #UserPassesTestMixin,
    template_name = 'metrics/klass_metrics.html'

    def get_context_data(self, **kwargs):
        context = super(KlassMetricsView, self).get_context_data(**kwargs)
        klass_pk = self.kwargs['klass_pk']
        try:
            klass = Klass.objects.get(pk=klass_pk)
            context['klass'] = klass
        except ObjectDoesNotExist:
            raise Http404
        return context

#    def test_func(self):
#        definition_pk = self.kwargs.get('definition_pk')
#        try:
#            definition = Definition.objects.get(pk=definition_pk)
#        except ObjectDoesNotExist:
#            raise Http404('Definition object not found')
#        if self.request.user.instructor:
#            if self.request.user.instructor == definition.klass.instructor:
#                print('User is instructor of class.')
#                return True
#        try:
#            if self.request.user.klass_memberships.get(klass__pk=definition.klass.pk):
#                print('User is student of class.')
#                return True
#        except ObjectDoesNotExist:
#            return False
#        return False
