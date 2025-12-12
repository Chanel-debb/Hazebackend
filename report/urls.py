from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportViewSet, get_all_reports, update_report_status

router = DefaultRouter()
router.register(r'reports', ReportViewSet, basename='reports')

urlpatterns = [
    path('', include(router.urls)),
    path('all-reports/', get_all_reports, name='all-reports'),
    path('update-report/<int:report_id>/', update_report_status, name='update-report-status'),
]
