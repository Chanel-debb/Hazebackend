from django.db import models
import uuid
from django.utils import timezone
from user.models import User


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
    updated_at = models.DateTimeField(null=True, blank=True)


    def save(self, *args, **kwargs):
        if self.id:
            self.updated_at = timezone.now()
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
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.id:
            self.updated_at = timezone.now()
        return super().save(*args, **kwargs)





class EstatePayment(models.Model):
    class Frequency(models.TextChoices):
        ONE_TIME = "One-Time", "One-Time",
        WEEKLY = "Weekly", "Weekly",
        QUARTERLY = "Quarterly", "Quarterly"
        MONTHLY = "Monthly", "Monthly"
        YEARLY = "Yearly", "Yearly"
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=10, choices=Frequency.choices, default=Frequency.ONE_TIME)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return self.title

class PaymentTransaction(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        SUCCESSFUL = "Successful", "Successful"
        FAILED = "Failed", "Failed"
        CANCELED = "Canceled", "Canceled"
    id = models.AutoField(primary_key=True)
    payment = models.ForeignKey(EstatePayment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reference = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reference
