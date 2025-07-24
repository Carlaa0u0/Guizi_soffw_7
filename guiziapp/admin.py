# guiziapp/admin.py
from django.contrib import admin
from .models import Categoria, Quiz, Pregunta, OpcionRespuesta, IntentoQuiz, RespuestaUsuario, UserProfile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# --- Administración del Perfil de Usuario ---
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'perfil de usuario'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')

    def get_role(self, obj):
        return obj.userprofile.role if hasattr(obj, 'userprofile') else 'N/A'
    get_role.short_description = 'Rol'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# --- Inlines para Quizzes y Contenido (Definir antes de las clases ModelAdmin que los usan) ---

class OpcionRespuestaInline(admin.TabularInline):
    model = OpcionRespuesta
    extra = 4 # Muestra 4 campos de opciones por defecto
    min_num = 4 # Requiere al menos 4 opciones
    max_num = 4 # Solo permite 4 opciones
    can_delete = False # No permitir eliminar opciones individualmente

class PreguntaInline(admin.StackedInline): # StackedInline para mejor visualización si hay mucho texto/imagen
    model = Pregunta
    inlines = [OpcionRespuestaInline] # <--- ¡ESTA LÍNEA ES CLAVE PARA ANIDAR OPCIONES!
    extra = 1 # Muestra 1 campo de pregunta por defecto
    min_num = 1 # Puedes establecer un mínimo si cada quiz debe tener X preguntas
    max_num = 10 # Tu requisito de 10 preguntas por quiz

class RespuestaUsuarioInline(admin.TabularInline):
    model = RespuestaUsuario
    extra = 0 # No mostrar campos extra vacíos
    readonly_fields = ('pregunta', 'opcion_seleccionada', 'es_correcta', 'tiempo_respuesta_segundos')
    can_delete = False # No permitir eliminar respuestas individuales de un intento


# --- Administración de Quizzes y Contenido (Clases ModelAdmin) ---

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'creador', 'fecha_creacion')
    list_filter = ('categoria', 'creador', 'fecha_creacion')
    search_fields = ('titulo', 'descripcion')
    inlines = [PreguntaInline] # <--- ¡Y ESTA LÍNEA ES CLAVE PARA ANIDAR PREGUNTAS EN EL QUIZ!
    fieldsets = (
        (None, {
            'fields': ('titulo', 'descripcion', 'categoria', 'creador')
        }),
    )

    # Autopoblar el creador si el usuario actual es staff
    def save_model(self, request, obj, form, change):
        if not obj.creador and request.user.is_staff: # Solo si no está asignado y el usuario es staff
            obj.creador = request.user
        super().save_model(request, obj, form, change)


@admin.register(IntentoQuiz)
class IntentoQuizAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'get_player_name_display_for_admin', 'puntaje', 'tiempo_transcurrido_segundos', 'completado', 'fecha_finalizacion')
    list_filter = ('quiz', 'completado', 'fecha_inicio')
    search_fields = ('quiz__titulo', 'usuario__username', 'nombre_anonimo')
    readonly_fields = ('puntaje', 'tiempo_transcurrido_segundos', 'fecha_inicio', 'fecha_finalizacion', 'completado')
    inlines = [RespuestaUsuarioInline]

    # Este método será llamado por 'list_display' en IntentoQuizAdmin
    def get_player_name_display_for_admin(self, obj):
        return obj.get_player_name() # Llama al método del modelo IntentoQuiz
    get_player_name_display_for_admin.short_description = 'Jugador' # Nombre de la columna en el admin


@admin.register(RespuestaUsuario)
class RespuestaUsuarioAdmin(admin.ModelAdmin):
    list_display = ('intento_quiz', 'pregunta', 'opcion_seleccionada', 'es_correcta', 'tiempo_respuesta_segundos')
    list_filter = ('es_correcta', 'intento_quiz__quiz')
    search_fields = ('pregunta__texto_pregunta', 'intento_quiz__quiz__titulo')
    readonly_fields = ('intento_quiz', 'pregunta', 'opcion_seleccionada', 'es_correcta', 'tiempo_respuesta_segundos')