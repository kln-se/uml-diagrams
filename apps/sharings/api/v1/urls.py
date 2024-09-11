from django.urls import include, path
from rest_framework import routers

from apps.sharings.api.v1 import views

router = routers.SimpleRouter()
router.register(r"", views.SharingViewSet)

urlpatterns = [path("", include(router.urls))]
