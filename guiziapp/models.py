from django.db import models
from django.db import models
from django.contrib.auth.models import User

class Actividad(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='actividades/')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

# Create your models here.
