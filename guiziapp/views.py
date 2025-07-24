from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout # Asegúrate de que 'logout' esté importado aquí
from django.contrib import messages

from guiziapp.forms import CustomSignupForm
from .models import Actividad
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User       



def home(request):
    return render(request, 'home.html')

def sobre_nosotros(request):
    return render(request, 'sobre_nosotros.html')

def signup_view(request):
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Cuenta creada con éxito!')
            return redirect('guiziapp:login')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
            data = request.POST.copy()
            data['email'] = ''
            data['password1'] = ''
            data['password2'] = ''
            form = CustomSignupForm(data)
    else:
        form = CustomSignupForm()
    return render(request, 'signup.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Buscar el usuario por correo
            user_obj = User.objects.get(email=email)
            username = user_obj.username  # Obtener el username real

            # Autenticación usando username
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, '¡Has iniciado sesión correctamente!')
                return redirect('guiziapp:home')  # Cambia si tu URL de inicio tiene otro nombre
            else:
                messages.error(request, 'Correo o contraseña incorrectos.')

        except User.DoesNotExist:
            messages.error(request, 'No existe un usuario registrado con ese correo.')

    return render(request, 'login.html')

# ¡¡¡DEBES AÑADIR ESTA FUNCIÓN!!!
def logout_view(request):
    logout(request) # Llama a la función de Django para cerrar la sesión
    messages.info(request, 'Has cerrado sesión exitosamente.') # Opcional: mensaje de confirmación
    return redirect('guiziapp:login') # Redirige al usuario a la página de login después de cerrar sesión




def lista_actividades_view(request):
   # Para pruebas, muestra todas las actividades en ambas secciones
    actividades_participando = Actividad.objects.all()
    actividades_creadas = Actividad.objects.all()

    return render(request, 'lista_actividades.html', {
        'actividades_participando': actividades_participando,
        'actividades_creadas': actividades_creadas
})

def mis_actividades_view(request):
    # Aquí iría la lógica para manejar las actividades.
    # Por ahora, simplemente renderiza una plantilla de actividades.
    return render(request, 'mis_actividades.html')