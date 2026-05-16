from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.views import View
from django.contrib import messages
from .models import User

class UserLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('portal-index')
        return render(request, 'accounts/login.html')

    def post(self, request):
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        
        user = authenticate(request, phone_number=phone_number, password=password)
        if user is not None:
            login(request, user)
            return redirect('portal-index')
        else:
            messages.error(request, "Invalid phone number or password")
            return render(request, 'accounts/login.html')

class UserRegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('portal-index')
        return render(request, 'accounts/register.html')

    def post(self, request):
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'accounts/register.html')

        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "Phone number already registered")
            return render(request, 'accounts/register.html')

        user = User.objects.create_user(phone_number=phone_number, password=password)
        login(request, user)
        messages.success(request, "Registration successful!")
        return redirect('portal-index')

from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

class UserLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')

class UserPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('profile')
    
    def form_valid(self, form):
        messages.success(self.request, "Password changed successfully!")
        return super().form_valid(form)
