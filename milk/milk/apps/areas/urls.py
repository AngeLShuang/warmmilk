from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()

router.register('areas', views.AreasViewSet,base_name="area")

urlpatterns = [
    path('', include(router.urls)),
]
