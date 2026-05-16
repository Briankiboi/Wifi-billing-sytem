from rest_framework import generics, permissions
from apps.packages.models import Package
from apps.billing.serializers import PackageSerializer

class PackageListView(generics.ListAPIView):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [permissions.AllowAny]
