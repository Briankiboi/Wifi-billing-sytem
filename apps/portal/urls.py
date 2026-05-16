from django.urls import path
from .views import PortalIndexView, PortalSuccessView, AboutView, ContactView, ProfileView

urlpatterns = [
    path('', PortalIndexView.as_view(), name='portal-index'),
    path('success/', PortalSuccessView.as_view(), name='portal-success'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
