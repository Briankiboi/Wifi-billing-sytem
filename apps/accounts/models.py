from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)

class User(AbstractUser):
    username = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=15, unique=True, db_index=True)
    email = models.EmailField(blank=True, null=True)
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = UserManager()
    
    @property
    def formatted_phone(self):
        """Returns phone number without 0 or 254 prefix for the UI input"""
        phone = str(self.phone_number)
        if phone.startswith('254'):
            return phone[3:]
        if phone.startswith('0'):
            return phone[1:]
        return phone

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class UserDevice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    mac_address = models.CharField(max_length=17, unique=True, db_index=True)
    device_name = models.CharField(max_length=100, blank=True, null=True)
    last_seen = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.mac_address = self.mac_address.upper().replace('-', ':')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.device_name or 'Unknown Device'} ({self.mac_address})"
