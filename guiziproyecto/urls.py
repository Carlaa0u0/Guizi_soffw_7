# tu_proyecto/urls.py

"""
URL configuration for proyecto_Dsfw_7 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include

# IMPORTACIONES NECESARIAS PARA SERVIR ARCHIVOS ESTÁTICOS Y DE MEDIOS EN DESARROLLO
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('guiziapp.urls')),  # Rutas de la app 'guiziapp'
    # Tus rutas de 'accounts' - mantenidas para compatibilidad si las necesitas
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/login/', lambda request: redirect('/login/')),
]

# ESTE BLOQUE ES CRÍTICO para servir archivos estáticos y de medios en modo de desarrollo (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)