from django.urls import path, include
from apps.diagrams.api.v1 import views
from rest_framework import routers


router = routers.SimpleRouter()
router.register(r'', views.DiagramViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('<int:pk>/copy/', views.DiagramCopyAPIView.as_view()),
]
