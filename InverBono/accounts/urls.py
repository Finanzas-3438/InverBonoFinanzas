from django.shortcuts import redirect
from django.urls import path
from .views import login_view, perfil_view, signup_view,dashboard_view, logout_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('', lambda request: redirect('login')),
    path('perfil/', perfil_view, name='perfil'),
    path('signup/', signup_view, name='signup'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('logout/', logout_view, name='logout'), 

]
