from django.urls import include, path
from rest_framework import routers

from apps.diagrams.api.v1 import views

router = routers.SimpleRouter()
router.register(r"", views.DiagramViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("<int:pk>/copy/", views.DiagramCopyAPIView.as_view(), name="diagram-copy"),
]
