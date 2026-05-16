import uuid
from django.db import models
from django.conf import settings
from apps.packages.models import Package
from apps.routers.models import Router
from apps.accounts.models import UserDevice

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='transactions')
    user_phone = models.CharField(max_length=15, db_index=True)
    user_mac = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    package = models.ForeignKey(Package, on_delete=models.PROTECT)
    router = models.ForeignKey(Router, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    checkout_request_id = models.CharField(max_length=100, unique=True, db_index=True)
    mpesa_code = models.CharField(max_length=50, blank=True, null=True, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

class Voucher(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=12, unique=True, db_index=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    is_used = models.BooleanField(default=False, db_index=True)
    used_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} ({self.package.name})"

class HotspotSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    device = models.ForeignKey(UserDevice, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    router = models.ForeignKey(Router, on_delete=models.CASCADE)
    transaction = models.OneToOneField(Transaction, on_delete=models.SET_NULL, null=True, blank=True)
    voucher = models.OneToOneField(Voucher, on_delete=models.SET_NULL, null=True, blank=True)
    
    start_time = models.DateTimeField(auto_now_add=True, db_index=True)
    end_time = models.DateTimeField(db_index=True)
    mikrotik_id = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['is_active', 'end_time']),
        ]

class BandwidthUsage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(HotspotSession, on_delete=models.CASCADE, related_name='usage_logs')
    bytes_in = models.BigIntegerField(default=0) # Upload
    bytes_out = models.BigIntegerField(default=0) # Download
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        get_latest_by = 'timestamp'
