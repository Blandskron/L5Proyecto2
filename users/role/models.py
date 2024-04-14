from django.db import models
from django.contrib.auth.models import User

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

    def __str__(self):
        return self.nombre

class PermisoProducto(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    puede_agregar = models.BooleanField(default=False)
    puede_cambiar = models.BooleanField(default=False)
    puede_eliminar = models.BooleanField(default=False)
    puede_ver = models.BooleanField(default=True)
    