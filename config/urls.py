from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from apps.core.views import CustomHttpErrorViews

api_v1_urlpatterns = [
    # API docs
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional API docs UI:
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
    # Apps
    path("users/", include("apps.users.api.v1.urls")),
    path("diagrams/", include("apps.diagrams.api.v1.urls")),
    path("auth/", include("apps.authentication.api.v1.urls")),
    path("sharings/", include("apps.sharings.api.v1.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(api_v1_urlpatterns)),
    path("health-check/", include("apps.core.urls")),
    # Prometheus metrics
    path("", include("django_prometheus.urls")),
]

# Should be overridden here, according to:
# https://docs.djangoproject.com/en/5.0/topics/http/views/#customizing-error-views
handler400 = CustomHttpErrorViews.bad_request_view
handler403 = CustomHttpErrorViews.permission_denied_view
handler404 = CustomHttpErrorViews.page_not_found_view
handler500 = CustomHttpErrorViews.server_error_view
