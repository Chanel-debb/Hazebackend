from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Report
from .serializers import (
    ReportSerializer, 
    ReportCreateSerializer, 
    ReportListSerializer,
    ReportUpdateSerializer
)
from user.permissions import IsAdminOrModeratorUser

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'category', 'location']
    ordering_fields = ['created_at', 'priority', 'status']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReportCreateSerializer
        elif self.action == 'list':
            return ReportListSerializer
        elif self.action in ['update', 'partial_update']:
            return ReportUpdateSerializer
        return ReportSerializer
    
    def get_queryset(self):
        # Skip for Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Report.objects.none()

        user = self.request.user

        # Prevent AnonymousUser errors
        if not user.is_authenticated:
            return Report.objects.none()

        # Admin or security can see all
        if user.role in ['admin', 'security']:
            return Report.objects.all()

        # Regular users see only their reports
        return Report.objects.filter(user=user)

    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_reports(self, request):
        """Get current user's reports"""
        reports = Report.objects.filter(user=request.user)
        serializer = ReportListSerializer(reports, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending reports (admin only)"""
        if request.user.role not in ['admin', 'security']:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        reports = Report.objects.filter(status='pending')
        serializer = ReportListSerializer(reports, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsAdminOrModeratorUser])
    def resolve(self, request, pk=None):
        """Mark a report as resolved"""
        report = self.get_object()
        report.status = 'resolved'
        report.resolved_at = timezone.now()
        report.save()
        
        serializer = ReportSerializer(report)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get report statistics (admin only)"""
        if request.user.role not in ['admin', 'security']:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = {
            'total': Report.objects.count(),
            'pending': Report.objects.filter(status='pending').count(),
            'in_progress': Report.objects.filter(status='in_progress').count(),
            'resolved': Report.objects.filter(status='resolved').count(),
            'by_category': {
                'maintenance': Report.objects.filter(category='maintenance').count(),
                'security': Report.objects.filter(category='security').count(),
                'cleanliness': Report.objects.filter(category='cleanliness').count(),
                'other': Report.objects.filter(category='other').count(),
            },
            'by_priority': {
                'high': Report.objects.filter(priority='High').count(),
                'medium': Report.objects.filter(priority='Medium').count(),
                'low': Report.objects.filter(priority='Low').count(),
            }
        }
        
        return Response(stats)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_reports(request):
    """Get all reports for admin dashboard with optional status filter"""
    
    # Check if user is admin or security
    if request.user.role not in ['admin', 'security']:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get status filter from query params (e.g., ?status=pending)
    status_filter = request.GET.get('status', None)
    
    if status_filter:
        reports = Report.objects.filter(status=status_filter).select_related('user')
    else:
        reports = Report.objects.all().select_related('user')
    
    reports = reports.order_by('-created_at')
    serializer = ReportSerializer(reports, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_report_status(request, report_id):
    """Update report status and admin notes"""
    
    # Check if user is admin or security
    if request.user.role not in ['admin', 'security']:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        report = Report.objects.get(id=report_id)
    except Report.DoesNotExist:
        return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Update status if provided
    new_status = request.data.get('status')
    if new_status:
        report.status = new_status
        
        # Set resolved_at if status is resolved or closed
        if new_status in ['resolved', 'closed'] and not report.resolved_at:
            report.resolved_at = timezone.now()
    
    # Update admin notes if provided
    admin_notes = request.data.get('admin_notes')
    if admin_notes:
        report.admin_notes = admin_notes
    
    # Assign to admin if provided
    assigned_to_id = request.data.get('assigned_to')
    if assigned_to_id:
        try:
            from user.models import User
            assigned_user = User.objects.get(id=assigned_to_id)
            report.assigned_to = assigned_user
        except User.DoesNotExist:
            pass
    
    report.save()
    serializer = ReportSerializer(report)
    
    return Response(serializer.data, status=status.HTTP_200_OK)