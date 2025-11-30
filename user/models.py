from django.db import models
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


class AppUserManager(BaseUserManager):
    def create_user(self, email, phone_number=None, first_name=None, last_name=None, other_names=None, password=None):
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
            other_names=other_names  # Fixed: was 'other_name'
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number, password=None):
        # Require phone_number
        if not phone_number:
            raise ValueError("Superuser must have a phone number")

        user = self.create_user(
            email=email,
            phone_number=phone_number,
            password=password,
            first_name="",
            last_name="",
            other_names=""  # Fixed: was 'other_name'
        )
        user.is_superuser = True
        user.is_staff = True
        user.role = User.Role.ADMIN
        user.save(using=self._db)
        return user

    


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"  # Changed: lowercase 'admin'
        SECURITY = "security", "Security"  # Changed: added security role
        RESIDENT = "resident", "Resident"  # Changed: from BASE to RESIDENT
    
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    other_names = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.RESIDENT)  # Changed default
    receipt_id = models.CharField(max_length=100, null=True, blank=True, unique=True)  # Fixed typo: reciept -> receipt
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone_number"]
    objects = AppUserManager()

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if self.id:
            self.updated_at = timezone.now()
        return super().save(*args, **kwargs)