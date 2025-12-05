from django.urls import path,
from rest_framework.routers import DefaultRouter
from .views import ReportViewSet

router = DefaultRouter()
router.register('reports', ReportViewSet, basename='report')

urlpatterns = [
    path('report/', report(), name='report'),
]