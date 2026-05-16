from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from apps.billing.models import Transaction, HotspotSession
from apps.routers.models import Router
from apps.packages.models import Package
from apps.accounts.models import User
from datetime import timedelta

@staff_member_required
def admin_dashboard(request):
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=7)

    # 1. Key Metrics
    total_revenue = Transaction.objects.filter(status='COMPLETED').aggregate(Sum('amount'))['amount__sum'] or 0
    today_revenue = Transaction.objects.filter(status='COMPLETED', created_at__date=today).aggregate(Sum('amount'))['amount__sum'] or 0
    active_sessions = HotspotSession.objects.filter(is_active=True).count()
    online_routers = Router.objects.filter(is_online=True).count()
    failed_payments = Transaction.objects.filter(status='FAILED', created_at__date=today).count()

    # 2. Revenue Chart Data (Last 7 Days)
    chart_data = []
    chart_labels = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        rev = Transaction.objects.filter(status='COMPLETED', created_at__date=day).aggregate(Sum('amount'))['amount__sum'] or 0
        chart_labels.append(day.strftime('%a'))
        chart_data.append(float(rev))

    # 3. Top Packages
    top_packages = Package.objects.annotate(
        sales_count=Count('transaction', filter=Q(transaction__status='COMPLETED'))
    ).order_by('-sales_count')[:5]

    # 4. Recent Failed Transactions
    recent_failures = Transaction.objects.filter(status='FAILED').order_by('-created_at')[:5]

    context = {
        'total_revenue': total_revenue,
        'today_revenue': today_revenue,
        'active_sessions': active_sessions,
        'online_routers': online_routers,
        'failed_payments': failed_payments,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'top_packages': top_packages,
        'recent_failures': recent_failures,
    }
    return render(request, 'dashboard/index.html', context)

@staff_member_required
def admin_routers(request):
    routers = Router.objects.all().order_by('-last_seen')
    context = {'routers': routers}
    return render(request, 'dashboard/routers.html', context)

@staff_member_required
def admin_transactions(request):
    transactions = Transaction.objects.all().order_by('-created_at')
    context = {'transactions': transactions}
    return render(request, 'dashboard/transactions.html', context)

@staff_member_required
def admin_packages(request):
    packages = Package.objects.all().order_by('-price')
    context = {'packages': packages}
    return render(request, 'dashboard/packages.html', context)

@staff_member_required
def package_edit(request, pk):
    package = get_object_or_404(Package, pk=pk)
    if request.method == 'POST':
        package.name = request.POST.get('name')
        package.price = request.POST.get('price')
        package.mbps_down = request.POST.get('mbps_down')
        package.duration_minutes = request.POST.get('duration_minutes')
        package.save()
        return redirect('admin-packages')
    return render(request, 'dashboard/package_form.html', {'package': package})

@staff_member_required
def admin_users(request):
    users = User.objects.all().annotate(
        total_spent=Sum('transactions__amount', filter=Q(transactions__status='COMPLETED')),
        session_count=Count('hotspotsession')
    ).order_by('-date_joined')
    return render(request, 'dashboard/users.html', {'users': users})

@staff_member_required
def admin_user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    sessions = HotspotSession.objects.filter(user=user).order_by('-start_time')
    transactions = Transaction.objects.filter(user_phone=user.phone_number).order_by('-created_at')
    context = {
        'target_user': user,
        'sessions': sessions,
        'transactions': transactions
    }
    return render(request, 'dashboard/user_detail.html', context)
