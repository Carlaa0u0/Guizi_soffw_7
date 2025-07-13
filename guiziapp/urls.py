from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views 


app_name = 'guiziapp'

urlpatterns = [
    path('', views.home, name='home'),
    path('sobre-nosotros/', views.sobre_nosotros, name='sobre_nosotros'),
    path('lista_actividades/', views.lista_actividades_view, name='lista_actividades'),
    path('mis_actividades/', views.lista_actividades_view, name='mis_actividades'),  # Puedes cambiar esto según tu lógica
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),  # Tu vista personalizada
    path('logout/', views.logout_view, name='logout'),  # También puedes personalizar logout
]