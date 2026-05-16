from django.urls import path
from apps.billing.views import STKPushView, MpesaCallbackView

urlpatterns = [
    path('stk-push/', STKPushView.as_view(), name='stk-push'),
    path('callback/', MpesaCallbackView.as_view(), name='mpesa-callback'),
]
