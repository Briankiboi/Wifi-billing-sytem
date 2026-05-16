from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.packages.models import Package
from apps.billing.models import HotspotSession
from django.utils import timezone

class PortalIndexView(LoginRequiredMixin, View):
    login_url = 'login'
    
    def get(self, request):
        mac = request.GET.get('mac', '00:00:00:00:00:00')
        packages = Package.objects.all().order_by('price')
        router_id = request.GET.get('router_id', '1')
        
        # Check for active session
        session = HotspotSession.objects.filter(
            device__mac_address=mac,
            is_active=True,
            end_time__gt=timezone.now()
        ).first()

        if session:
            return render(request, 'portal/status.html', {
                'session': session,
                'mac': mac
            })

        context = {
            'mac': mac,
            'packages': packages,
            'router_id': router_id,
        }
        return render(request, 'portal/index.html', context)

class AboutView(View):
    def get(self, request):
        return render(request, 'portal/about.html')

class ContactView(View):
    def get(self, request):
        return render(request, 'portal/contact.html')

class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        # Fetch active sessions for the user
        active_sessions = HotspotSession.objects.filter(
            user=request.user,
            is_active=True,
            end_time__gt=timezone.now()
        ).order_by('-start_time')

        # Fetch past sessions (Purchase history)
        past_sessions = HotspotSession.objects.filter(
            user=request.user
        ).order_by('-start_time')

        return render(request, 'portal/profile.html', {
            'active_sessions': active_sessions,
            'past_sessions': past_sessions
        })

class PortalSuccessView(View):
    def get(self, request):
        context = {
            'mac': request.GET.get('mac'),
            'link_orig': request.GET.get('link-orig', 'http://google.com'),
        }
        return render(request, 'portal/success.html', context)
