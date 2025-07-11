"""InverBono URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView 
from accounts import views as account_views
from django.shortcuts import render

def custom_404(request, exception=None):
    return render(request, '404.html', status=404)

handler404 = custom_404

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', account_views.login_view, name='login'),
    path('perfil/', account_views.perfil_view, name='perfil'),
    path('signup/', account_views.signup_view, name='signup'),
    path('dashboard/', account_views.dashboard_view, name='dashboard'),
    path('logout/', account_views.logout_view, name='logout'),

    path('bonds/', include('bonds.urls')),

    path('', RedirectView.as_view(url='/dashboard/', permanent=False), name='index'),
    ]
