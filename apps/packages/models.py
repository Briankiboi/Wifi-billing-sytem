from django.db import models
import uuid

class Package(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField(help_text="Format: DD HH:MM:SS")
    bandwidth_limit_up = models.IntegerField(help_text="In kbps (e.g. 1024 for 1Mbps)", default=1024)
    bandwidth_limit_down = models.IntegerField(help_text="In kbps (e.g. 1024 for 1Mbps)", default=1024)
    description = models.TextField(blank=True, null=True)

    @property
    def mbps_up(self):
        return round(self.bandwidth_limit_up / 1024, 1)

    @property
    def mbps_down(self):
        return round(self.bandwidth_limit_down / 1024, 1)

    def __str__(self):
        return f"{self.name} - KES {self.price}"
