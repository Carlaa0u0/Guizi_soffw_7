# guiziapp/urls.py
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView # Importa LogoutView

app_name = 'guiziapp'

urlpatterns = [
    # Rutas de páginas generales (tus existentes)
    path('', views.home, name='home'),
    path('sobre-nosotros/', views.sobre_nosotros, name='sobre_nosotros'),

    # Rutas de Autenticación (respetando tu implementación)
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='guiziapp:home'), name='logout'),

    # --- RUTAS PARA LOS QUIZZES Y RANKING ---
    # La página principal para listar quizzes por categoría
    path('quizzes/', views.lista_quizzes_view, name='lista_quizzes'),

    # Las rutas para crear y editar quizzes han sido ELIMINADAS.
    # path('quizzes/crear/', views.crear_quiz_view, name='crear_quiz'), # ELIMINADA
    # path('quizzes/<int:quiz_id>/editar/', views.editar_quiz_view, name='editar_quiz'), # ELIMINADA

    # Rutas para jugar un quiz
    path('quizzes/<int:quiz_id>/iniciar/', views.iniciar_quiz_view, name='iniciar_quiz'),
    path('quizzes/pedir-nombre/', views.pedir_nombre_anonimo_view, name='pedir_nombre_anonimo'),
    path('quizzes/<int:quiz_id>/jugar/', views.jugar_quiz_view, name='jugar_quiz'),
    path('quizzes/procesar-respuesta/', views.procesar_respuesta_quiz_ajax, name='procesar_respuesta_quiz_ajax'),
    path('quizzes/resultados/<int:intento_quiz_id>/', views.resultados_quiz_view, name='resultados_quiz'),

    # Ruta para el ranking global
    path('ranking/', views.ranking_view, name='ranking'),

    # Ruta para "Mis Actividades" (ahora se centra en el historial de juego del usuario)
    path('mis-actividades/', views.mis_actividades_view, name='mis_actividades'), # Mantengo el nombre original para tus enlaces
]