from django.db import models
import uuid
from django.utils import timezone


def access_code():
    code = str(uuid.uuid4())
    return f"AC{code[:10].upper()}"


class Vistor(models.Model):
    id = models.AutoField(primary_key=True)
    fullname = models.CharField(max_length=100)
    phone_number = models.JSONField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    signed_in = models.DateTimeField(null=True, blank=True)
    signed_out = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.fullname
    

# AccessCode and Annoucement


class AccessCode(models.Model):
    class Type(models.TextChoices):
        DAILY = "Daily", "Daily"
        WEEKLY = "Weekly", "Weekly"
        MONTHLY = "Monthly", "Monthly"
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    code_type = models.CharField(max_length=10, choices=Type.choices, default=Type.MONTHLY)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    code = models.CharField(max_length=12, unique=True, null=True, blank=True)
    status = models.BooleanField(default=True)


    def save(self, *args, **kwargs):
        if self:
            self.code = access_code()
        if self.end_time == timezone.now():
            self.status = False
        return super().save(*args, **kwargs)
    

    def __str__(self):
        return self.code
    
    class Meta:
        ordering = ['-created_at']


class Announcement(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    signed_by = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
