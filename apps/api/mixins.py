from django.http import Http404

from apps.klasses.models import Klass


class OwnerPermissionCheckMixin(object):
    def get_queryset(self):
        print(self.request.user)
        if self.request.user.is_anonymous:
            return None
        print(dir(self.serializer_class))
        temp_model = self.serializer_class.Meta.model
        if hasattr(temp_model, 'creator') or hasattr(temp_model, 'instructor'):
            print(temp_model)
            if self.request.user.is_superuser:
                return temp_model.objects.all()
            else:
                if temp_model == Klass:
                    # return temp_model.objects.filter(instructor__user=self.request.user)
                    kwargs = {'instructor__user': self.request.user}
                else:
                    # return temp_model.objects.filter(creator__user=self.request.user)
                    kwargs = {'creator__user': self.request.user}
                return temp_model.objects.filter(**kwargs)

        else:
            return super().get_queryset()
