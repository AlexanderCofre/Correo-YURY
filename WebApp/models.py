from django.db import models
from django.contrib.auth.models import AbstractUser

# Modelo para áreas/departamentos
class Departamento(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    numero = models.PositiveIntegerField()  # Número del departamento, puede ser usado como un identificador único o número de piso

    def __str__(self):
        return f"{self.nombre} (Nº {self.numero})"

# Modelo de Área y referencia al departamento
class Area(models.Model):
    nombre = models.CharField(max_length=50)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name="areas")

    def __str__(self):
        return f"{self.nombre} - {self.departamento.nombre}"

# Modelo de Cargo, ahora depende de Área
class Cargo(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="cargos")  # Relación con Área

    def __str__(self):
        return self.nombre

# Modelo personalizado de usuario que hereda de AbstractUser
class Trabajador(AbstractUser):
    RUT = models.CharField(max_length=12, unique=True)
    first_name = models.CharField(max_length=30, blank=True)  
    last_name = models.CharField(max_length=150, blank=True)  
    email = models.EmailField(max_length=254, unique=True, blank=True) 
    sexo = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Femenino')])
    fecha_ingreso = models.DateField(null=True, blank=True)
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE, null=True, blank=True, related_name="trabajadores")
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True, related_name="trabajadores")
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, null=True, blank=True, related_name="trabajadores")


    def __str__(self):
        return f"{self.first_name}, {self.last_name} ({self.RUT})"

# Modelo para los datos de contacto de emergencia
class ContactoEmergencia(models.Model):
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, related_name="contactos_emergencia")
    nombre_contacto = models.CharField(max_length=100)
    apellido_contacto = models.CharField(max_length=100)
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
