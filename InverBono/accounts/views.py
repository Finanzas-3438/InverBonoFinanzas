from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import login
from .models import User
from bonds.models import Bond

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'accounts/login.html', {'error': 'Credenciales incorrectas'})
    return render(request, 'accounts/login.html')

@login_required
def perfil_view(request):
    return render(request, 'accounts/perfil.html', {'user': request.user})



def signup_view(request):
    if request.method == 'POST':
        try:
            user = User.objects.create_user(
                email=request.POST['email'],
                password=request.POST['password'],
                nombres=request.POST['nombres'],
                apellidos=request.POST['apellidos'],
                tipo_documento=request.POST['tipo_documento'],
                documento=request.POST['documento'],
                celular=request.POST['celular'],
                direccion=request.POST['direccion']
            )
            login(request, user)
            return redirect('perfil')
        except Exception as e:
            return render(request, 'accounts/signup.html', {'error': str(e)})
    return render(request, 'accounts/signup.html')

@login_required
def dashboard_view(request):
    bonds = Bond.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/dashboard.html', {'bonds': bonds})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')