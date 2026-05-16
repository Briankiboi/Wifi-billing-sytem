from django.http import HttpResponseForbidden
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class MpesaIPWhitelistMiddleware:
    """
    Middleware to ensure M-PESA callbacks only come from Safaricom IPs.
    """
    SAFARICOM_IPS = [
        '196.201.214.200', '196.201.214.206', '196.201.213.114', 
        '196.201.214.207', '196.201.214.208', '196.201.213.44', 
        '196.201.212.127', '196.201.212.138', '196.201.212.129', 
        '196.201.212.136', '196.201.212.74', '196.201.212.69'
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/api/v1/payment/callback/':
            ip = self.get_client_ip(request)
            if settings.DEBUG: # Allow local testing
                return self.get_response(request)
                
            if ip not in self.SAFARICOM_IPS:
                logger.warning(f"Unauthorized M-PESA callback attempt from IP: {ip}")
                return HttpResponseForbidden("Unauthorized")
        
        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
