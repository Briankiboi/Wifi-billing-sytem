from django.db import models
import uuid
from apps.core.encryption import Encryptor

class RouterGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Router(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(RouterGroup, on_delete=models.SET_NULL, null=True, related_name='routers')
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.GenericIPAddressField(unique=True)
    api_port = models.IntegerField(default=8728)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=500) 
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['ip_address', 'is_online']),
        ]

    def save(self, *args, **kwargs):
        encryptor = Encryptor()
        if self.password and not self.password.startswith('gAAAA'):
            self.password = encryptor.encrypt(self.password)
        super().save(*args, **kwargs)

    @property
    def decrypted_password(self):
        return Encryptor().decrypt(self.password)

    def __str__(self):
        return f"{self.name} ({self.ip_address})"

class RouterLog(models.Model):
    LEVEL_CHOICES = (
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    router = models.ForeignKey(Router, on_delete=models.CASCADE, related_name='logs')
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='INFO')
    message = models.TextField()
    data = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
