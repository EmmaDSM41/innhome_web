from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import RegistroForm  

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Redirigir a la página principal o a donde desees
        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirigir a la página principal

def register_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)  # Usar el formulario personalizado
        if form.is_valid():
            user = form.save()
            login(request, user)  # Iniciar sesión automáticamente al registrarse
            return redirect('home')  # Redirigir a la página principal
    else:
        form = RegistroForm()  # Usar el formulario personalizado
    return render(request, 'registration/register.html', {'form': form})
