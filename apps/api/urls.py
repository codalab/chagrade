from django.conf.urls import url, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework.routers import SimpleRouter

# from apps.api.views.producers import ProducerViewSet
from apps.api.views.profiles import ProfileViewSet
from .views import competitions, profiles, search

app_name = 'api'
API_PREFIX = "v1"

# API routes
router = SimpleRouter()
router.register('users', ProfileViewSet)
# router.register('producers', ProducerViewSet)
# router.register('competitions', competitions.CompetitionViewSet)
# router.register('submissions', competitions.SubmissionViewSet)

# Documentation details
schema_view = get_schema_view(
    openapi.Info(
        title="Chagrade API",
        default_version='v1',
        description="Chagrade is a platform for machine learning resources, like competitions, test sets, and example solutions",
        contact=openapi.Contact(email="info@codalab.org"),
        license=openapi.License(name="MIT License"),
    ),
    validators=['flex', 'ssv'],
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    url('^', include(router.urls)),
    # url('query/', search.SearchView.as_view()),
    # url('my_profile/', profiles.GetMyProfile.as_view()),

    url('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Docs
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^$', schema_view.with_ui('swagger', cache_timeout=None), name='docs'),

    # Optionally, use "redoc" style
    # url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),
]
