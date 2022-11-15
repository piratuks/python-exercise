from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework import routers
from exercise.quickstart import views
from drf_yasg import openapi
from drf_yasg.views import get_schema_view as swagger_get_schema_view
from rest_framework import permissions

router = routers.DefaultRouter()
router.register(r'auth', views.AuthViewSet, basename='auth')
router.register(r'restaurants', views.RestaurantViewSet)
router.register(r'employee', views.EmployeeViewSet)

schema_view = swagger_get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='1.0.0',
        description="API documentation of Python APP (Exercise)",
        terms_of_service="https://www.linkedin.com/in/evaldas123456/",
        contact=openapi.Contact(email="evaldiz@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,)
)

urlpatterns = [
    path(
        'admin/',
        admin.site.urls),
    path(
        '',
        include(
            router.urls)),
    path(
        'documentation/',
        include(
            [
                re_path(
                    r'^swagger(?P<format>\.json|\.yaml)$',
                    schema_view.without_ui(
                        cache_timeout=0),
                    name='schema-json'),
                path(
                    'swagger/',
                    schema_view.with_ui(
                        'swagger',
                        cache_timeout=0),
                    name="swagger-schema"),
            ])),
    path(
        'api-auth/',
        include(
            'rest_framework.urls',
            namespace='rest_framework')),
]
