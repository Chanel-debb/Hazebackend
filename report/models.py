from django.db import models
from django.utils import timezone
from user.models import User  

class Report(models.Model):
    CATEGORY_CHOICES = [
        ('maintenance', 'Maintenance'),
        ('security', 'Security'),
        ('cleanliness', 'Cleanliness'),
        ('other', 'Other'),
    ]
    
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    # User who submitted the report
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    
    # Report details
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    image_description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='reports/', blank=True, null=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    # Admin response
    admin_notes = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_reports'
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.category} - {self.title} ({self.status})"