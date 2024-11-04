from django.db import models
from django.contrib.auth.models import AbstractUser

# Modelo personalizado de usuario que hereda de AbstractUser
class Trabajador(AbstractUser):
    RUT = models.CharField(max_length=12, unique=True)
    first_name = models.CharField(max_length=30, blank=True)  
    last_name = models.CharField(max_length=150, blank=True)  
    email = models.EmailField(max_length=254, unique=True, blank=True) 
    sexo = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Femenino')])
    fecha_ingreso = models.DateField()
    cargo = models.CharField(max_length=50)
    area = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nombre_completo} ({self.RUT})"

# Modelo para los datos de contacto de emergencia
class ContactoEmergencia(models.Model):
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, related_name="contactos_emergencia")
    nombre_contacto = models.CharField(max_length=100)
    relacion = models.CharField(max_length=50)
    telefono_contacto = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.nombre_contacto} - {self.relacion}"

# Modelo para las cargas familiares
class CargaFamiliar(models.Model):
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, related_name="cargas_familiares")
    nombre_carga = models.CharField(max_length=100)
    parentesco = models.CharField(max_length=50)
    sexo = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Femenino')])
    rut = models.CharField(max_length=12)

    def __str__(self):
        return f"{self.nombre_carga} - {self.parentesco}"

# Modelo para áreas/departamentos
class Departamento(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre
