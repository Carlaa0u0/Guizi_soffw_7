from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout # Asegúrate de que 'logout' esté importado aquí
from django.contrib import messages


def home(request):
    return render(request, 'home.html')

def sobre_nosotros(request):
    return render(request, 'sobre_nosotros.html')

def signup_view(request):
    # Por ahora, simplemente renderiza la plantilla de registro.
    # Aquí iría la lógica para manejar el formulario de registro.
    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, '¡Has iniciado sesión correctamente!')
            return redirect('guiziapp:home')  # Redirige al inicio después del login
        else:
            messages.error(request, 'Usuario o contraseña incorrectos. Por favor, inténtalo de nuevo.')

    return render(request, 'login.html')

# ¡¡¡DEBES AÑADIR ESTA FUNCIÓN!!!
def logout_view(request):
    logout(request) # Llama a la función de Django para cerrar la sesión
    messages.info(request, 'Has cerrado sesión exitosamente.') # Opcional: mensaje de confirmación
    return redirect('guiziapp:login') # Redirige al usuario a la página de login después de cerrar sesión

def lista_actividades_view(request):
    # Aquí iría la lógica para manejar la lista de actividades.
    # Por ahora, simplemente renderiza una plantilla de lista de actividades.
    return render(request, 'lista_actividades.html')    

def mis_actividades_view(request):
    # Aquí iría la lógica para manejar las actividades.
    # Por ahora, simplemente renderiza una plantilla de actividades.
    return render(request, 'mis_actividades.html')