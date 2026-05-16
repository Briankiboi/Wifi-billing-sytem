from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from apps.billing.serializers import STKPushSerializer, PackageSerializer
from apps.billing.models import Transaction
from apps.billing.mpesa import MpesaClient
from apps.billing.tasks import activate_internet_session
from apps.packages.models import Package
from apps.routers.models import Router
import logging

logger = logging.getLogger(__name__)

class STKPushView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = STKPushSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            package = Package.objects.get(id=serializer.validated_data['package_id'])
            router = Router.objects.get(id=serializer.validated_data['router_id'])
            user_mac = serializer.validated_data['user_mac']

            mpesa = MpesaClient()
            result = mpesa.stk_push(
                phone=phone,
                amount=package.price,
                reference=f"WiFi-{package.name}",
                description=f"WiFi Payment for {user_mac}"
            )

            if result and result.get('ResponseCode') == '0':
                # Create a pending transaction
                Transaction.objects.create(
                    user_phone=phone,
                    user_mac=user_mac,
                    checkout_request_id=result['CheckoutRequestID'],
                    merchant_request_id=result.get('MerchantRequestID'),
                    amount=package.price,
                    package=package,
                    router=router,
                    status='PENDING'
                )
                return Response(result, status=status.HTTP_200_OK)
            
            return Response({"error": "Failed to initiate M-PESA payment"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.db import transaction

class MpesaCallbackView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data.get('Body', {}).get('stkCallback', {})
        result_code = data.get('ResultCode')
        checkout_request_id = data.get('CheckoutRequestID')
        
        try:
            with transaction.atomic():
                tx = Transaction.objects.select_for_update().get(checkout_request_id=checkout_request_id)
                
                if result_code == 0:
                    # Payment Success
                    tx.status = 'COMPLETED'
                    metadata = data.get('CallbackMetadata', {}).get('Item', [])
                    for item in metadata:
                        if item.get('Name') == 'MpesaReceiptNumber':
                            tx.mpesa_code = item.get('Value')
                    tx.save()
                    
                    # Trigger activation - pass only ID for atomicity
                    activate_internet_session.delay(tx.id)
                    
                else:
                    # Payment Failed
                    tx.status = 'FAILED'
                    tx.result_description = data.get('ResultDesc')
                    tx.save()
                    
            return Response({"status": "received"}, status=status.HTTP_200_OK)
        except Transaction.DoesNotExist:
            return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)
