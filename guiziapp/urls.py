from django.contrib import admin
from django.urls import path, include
from . import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # Aquí enlazas la app guiziapp
    path('sobre-nosotros/', views.sobre_nosotros, name='sobre_nosotros'),
    path('signup/', views.signup_view, name='signup'),
    

]
