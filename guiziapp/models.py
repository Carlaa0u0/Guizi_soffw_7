

# guiziapp/models.py
from django.db import models
from django.contrib.auth.models import User # Usamos el modelo de usuario por defecto de Django



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20) # 'Profesor', 'Estudiante', etc.
    age = models.PositiveIntegerField() # Mantengo como lo enviaste, asumiendo que es obligatorio

    def __str__(self):
        return f"{self.user.username} Profile"

# --- Modelo 'Actividad' (Tal cual lo tienes, aunque no lo usaremos directamente para quizzes) ---
# Lo mantengo aquí porque lo enviaste, pero lo ideal es que lo uses para lo que originalmente fue diseñado.
# Para la funcionalidad de quizzes, usaremos los nuevos modelos de Categoria, Quiz, Pregunta, etc.
class Actividad(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='actividades/')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


# --- Modelos para Quizzes ---

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre

class Quiz(models.Model):
    titulo = models.CharField(max_length=200)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='quizzes')
    # Creador apunta directamente al modelo User de Django
    creador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='quizzes_creados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.titulo} ({self.categoria.nombre})"

class Pregunta(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='preguntas')
    texto_pregunta = models.TextField()
    imagen_pregunta = models.ImageField(upload_to='quiz_images/', blank=True, null=True)
    tiempo_limite = models.IntegerField(default=20) # Tiempo en segundos para responder la pregunta

    def __str__(self):
        return f"Q: {self.texto_pregunta[:70]}..."

class OpcionRespuesta(models.Model):
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name='opciones')
    texto_opcion = models.CharField(max_length=255)
    es_correcta = models.BooleanField(default=False)

    def __str__(self):
        return f"Opción: {self.texto_opcion} (Correcta: {self.es_correcta})"

class IntentoQuiz(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='intentos')
    nombre_anonimo = models.CharField(max_length=100, blank=True, null=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='intentos')
    puntaje = models.IntegerField(default=0)
    tiempo_transcurrido_segundos = models.IntegerField(default=0)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_finalizacion = models.DateTimeField(blank=True, null=True)
    completado = models.BooleanField(default=False)

    class Meta:
        ordering = ['-puntaje', 'tiempo_transcurrido_segundos']
        verbose_name_plural = "Intentos de Quizzes"

    def __str__(self):
        if self.usuario:
            return f"Intento de {self.usuario.username} en {self.quiz.titulo} - P: {self.puntaje}"
        return f"Intento de {self.nombre_anonimo} en {self.quiz.titulo} - P: {self.puntaje}"

    def get_player_name(self):
        return self.usuario.username if self.usuario else self.nombre_anonimo


class RespuestaUsuario(models.Model):
    intento_quiz = models.ForeignKey(IntentoQuiz, on_delete=models.CASCADE, related_name='respuestas_individuales')
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    opcion_seleccionada = models.ForeignKey(OpcionRespuesta, on_delete=models.CASCADE, null=True, blank=True)
    es_correcta = models.BooleanField(default=False)
    tiempo_respuesta_segundos = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Respuestas de Usuarios"

    def __str__(self):
        return f"Respuesta a '{self.pregunta.texto_pregunta[:30]}...' por {self.intento_quiz.get_player_name()}"