import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from datetime import timedelta



# Custom user manager
class AppUserManager(BaseUserManager):

    def create_user(
        self,
        email,
        phone_number=None,
        first_name=None,
        last_name=None,
        other_names=None,
        password=None
    ):
        if not email:
            raise ValueError("Email is required")
        if not password:
            raise ValueError("Password is required")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            other_names=other_names,
        )

        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)

        return user

    def create_superuser(self, email, phone_number, password=None):
        if not phone_number:
            raise ValueError("Superuser must have a phone number")

        user = self.create_user(
            email=email,
            phone_number=phone_number,
            password=password,
        )

        # Give admin rights
        user.is_superuser = True
        user.is_staff = True
        user.role = User.Role.ADMIN
        user.save(using=self._db)

        return user


# Custom user model
class User(AbstractBaseUser, PermissionsMixin):

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        SECURITY = "security", "Security"
        RESIDENT = "resident", "Resident"

    id = models.AutoField(primary_key=True)

    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    other_names = models.CharField(max_length=50, null=True, blank=True)

    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.RESIDENT
    )

    receipt_id = models.CharField(max_length=100, null=True, blank=True)

    # IMPORTANT FIELDS
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)        # REQUIRED TO LOGIN TO ADMIN
    is_active = models.BooleanField(default=True)        # REQUIRED TO LOGIN TO ADMIN

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone_number"]

    objects = AppUserManager()
    account_expiry_date = models.DateTimeField(null=True, blank=True)
    account_status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('expired', 'Expired'),
            ('archived', 'Archived'),
        ],
        default='active'
    )
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if self.id:
            self.updated_at = timezone.now()
        return super().save(*args, **kwargs)


# Visitors model
class Visitor(models.Model):
    id = models.AutoField(primary_key=True)
    fullname = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    signed_in = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.fullname

# receipt ID model
class ReceiptID(models.Model):
    class Type(models.TextChoices):
        OWNER = "owner", "Owner/Landlord"
        TENANT = "tenant", "Tenant"
    
    id = models.AutoField(primary_key=True)
    receipt_code = models.CharField(max_length=20, unique=True, editable=False)
    type = models.CharField(max_length=10, choices=Type.choices)
    is_used = models.BooleanField(default=False)
    used_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='receipt_used'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='receipts_created'
    )
    
    def save(self, *args, **kwargs):
        if not self.receipt_code:
            # Generate unique receipt code
            self.receipt_code = f"REC-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.receipt_code} ({self.get_type_display()})"
    
    class Meta:
        ordering = ['-created_at']

class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    email_updates = models.BooleanField(default=False)
    sms_alerts = models.BooleanField(default=False)
    system_alerts = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - Preferences"
    
    class Meta:
        verbose_name_plural = "User Preferences"
