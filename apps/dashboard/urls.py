from django.urls import path
from .views import (
    admin_dashboard, admin_routers, admin_transactions, 
    admin_packages, package_edit, admin_users, admin_user_detail
)

urlpatterns = [
    path('', admin_dashboard, name='admin-dashboard'),
    path('routers/', admin_routers, name='admin-routers'),
    path('transactions/', admin_transactions, name='admin-transactions'),
    path('packages/', admin_packages, name='admin-packages'),
    path('packages/<uuid:pk>/edit/', package_edit, name='package-edit'),
    path('users/', admin_users, name='admin-users'),
    path('users/<uuid:pk>/', admin_user_detail, name='admin-user-detail'),
]
