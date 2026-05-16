import requests
import base64
import logging
from datetime import datetime
from django.conf import settings
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)

class MpesaError(Exception):
    """Custom exception for M-PESA API errors."""
    pass

class MpesaClient:
    """Enhanced M-PESA client with status query and production security."""
    def __init__(self):
        self.consumer_key = settings.env('MPESA_CONSUMER_KEY')
        self.consumer_secret = settings.env('MPESA_CONSUMER_SECRET')
        self.shortcode = settings.env('MPESA_SHORTCODE')
        self.passkey = settings.env('MPESA_PASSKEY')
        self.env = settings.env('MPESA_ENVIRONMENT', default='sandbox')
        
        self.base_url = 'https://sandbox.safaricom.co.ke' if self.env == 'sandbox' else 'https://api.safaricom.co.ke'

    def get_access_token(self):
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        try:
            res = requests.get(url, auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret), timeout=10)
            res.raise_for_status()
            return res.json()['access_token']
        except Exception as e:
            logger.error(f"M-PESA Auth Error: {e}")
            raise MpesaError("Failed to authenticate with M-PESA")

    def get_password(self, timestamp):
        str_to_encode = f"{self.shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(str_to_encode.encode()).decode()

    def stk_push(self, phone, amount, reference, description):
        token = self.get_access_token()
        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": self.get_password(timestamp),
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone,
            "PartyB": self.shortcode,
            "PhoneNumber": phone,
            "CallBackURL": settings.env('MPESA_CALLBACK_URL'),
            "AccountReference": reference,
            "TransactionDesc": description
        }

        try:
            res = requests.post(url, json=payload, headers=headers, timeout=15)
            return res.json()
        except Exception as e:
            logger.error(f"STK Push Request Failed: {e}")
            raise MpesaError("M-PESA service unavailable")

    def query_stk_status(self, checkout_request_id):
        """Proactively checks the status of a transaction."""
        token = self.get_access_token()
        url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": self.get_password(timestamp),
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id
        }

        try:
            res = requests.post(url, json=payload, headers=headers, timeout=10)
            return res.json()
        except Exception as e:
            logger.error(f"Status Query Failed for {checkout_request_id}: {e}")
            return None
