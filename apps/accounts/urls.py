from django.urls import path
from .views import UserLoginView, UserRegisterView, UserLogoutView, UserPasswordChangeView

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('password-change/', UserPasswordChangeView.as_view(), name='password_change'),
]
