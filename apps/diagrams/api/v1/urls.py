from django.urls import path
from apps.diagrams.api.v1 import views

urlpatterns = [
    path('', views.DiagramViewSet.as_view(
        {
            'get': 'list',
            'post': 'create',
        }
    )),
    path('<int:pk>/', views.DiagramViewSet.as_view(
        {
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy',
        }
    )),
    path('<int:pk>/copy/', views.DiagramCopyAPIView.as_view()),
]
