from rest_framework import serializers
from apps.billing.models import Transaction
from apps.packages.models import Package

class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class STKPushSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    package_id = serializers.UUIDField()
    router_id = serializers.UUIDField()
    user_mac = serializers.CharField(max_length=20)
