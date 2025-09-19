# rct_dashboard/urls.py
from django.contrib import admin
from django.urls import path, include # Add include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')), # ADD THIS LINE

    path('', include('study.urls')),
]