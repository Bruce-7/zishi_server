from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'versions', views.AppVersionViewSet, basename='version')

urlpatterns = [
    path('', include(router.urls)),
]
