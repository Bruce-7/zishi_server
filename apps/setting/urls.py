from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'versions', views.AppVersionViewSet, basename='version')
router.register(r'configs', views.DynamicConfigViewSet, basename='config')

urlpatterns = [
    path('', include(router.urls)),
]
