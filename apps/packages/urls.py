from django.urls import path
from apps.packages.views import PackageListView

urlpatterns = [
    path('', PackageListView.as_view(), name='package-list'),
]
