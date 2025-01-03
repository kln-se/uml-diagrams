from django.urls import include, path
from rest_framework import routers

from apps.diagrams.api.v1 import views

router = routers.SimpleRouter()
router.register(
    r"shared-with-me", views.SharedWithMeDiagramViewSet, basename="shared-diagram"
)
router.register(r"", views.DiagramViewSet)
router.register(r"public", views.PublicDiagramViewSet, basename="public-diagram")

urlpatterns = [
    path("", include(router.urls)),
]
