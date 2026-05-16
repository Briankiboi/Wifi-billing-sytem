from django.test import TestCase, Client
from django.urls import reverse
from apps.billing.models import Transaction
from apps.packages.models import Package
from apps.routers.models import Router
import uuid

class MpesaCallbackTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.router = Router.objects.create(
            name="Test Router",
            ip_address="192.168.88.1",
            username="admin",
            password="password"
        )
        self.package = Package.objects.create(
            name="Test Plan",
            price=10.00,
            duration="01:00:00"
        )
        self.transaction = Transaction.objects.create(
            user_phone="254712345678",
            checkout_request_id="ws_CO_123456789",
            amount=10.00,
            package=self.package,
            router=self.router,
            status='PENDING'
        )

    def test_callback_success(self):
        url = reverse('mpesa-callback')
        payload = {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": "12345-67890-1",
                    "CheckoutRequestID": "ws_CO_123456789",
                    "ResultCode": 0,
                    "ResultDesc": "The service request is processed successfully.",
                    "CallbackMetadata": {
                        "Item": [
                            {"Name": "Amount", "Value": 10.00},
                            {"Name": "MpesaReceiptNumber", "Value": "RKL7OPQ9ST"},
                            {"Name": "TransactionDate", "Value": 20260515130000},
                            {"Name": "PhoneNumber", "Value": 254712345678}
                        ]
                    }
                }
            }
        }
        
        response = self.client.post(url, data=payload, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, 'COMPLETED')
        self.assertEqual(self.transaction.mpesa_code, 'RKL7OPQ9ST')

    def test_callback_failed(self):
        url = reverse('mpesa-callback')
        payload = {
            "Body": {
                "stkCallback": {
                    "CheckoutRequestID": "ws_CO_123456789",
                    "ResultCode": 1032,
                    "ResultDesc": "Request cancelled by user"
                }
            }
        }
        
        response = self.client.post(url, data=payload, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, 'FAILED')
