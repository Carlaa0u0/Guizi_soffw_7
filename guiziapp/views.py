from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib import messages

def home(request):
    return render(request, 'home.html')

def sobre_nosotros(request):
    return render(request, 'sobre_nosotros.html')

def signup_view(request):
    return render(request, 'signup.html')  # o lo que necesites

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # O correo si lo prefieres
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('guiziapp:home')  # Redirige a donde desees
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'guiziapp/login.html')

def logout_view(request):
    logout(request)
    return redirect('guiziapp:login')