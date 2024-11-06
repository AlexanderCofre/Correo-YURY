from django.contrib import admin
from .models import Trabajador, ContactoEmergencia, CargaFamiliar, Departamento

# Configuración para mostrar el modelo Trabajador
@admin.register(Trabajador)
class TrabajadorAdmin(admin.ModelAdmin):
    list_display = ('username', 'RUT', 'first_name', 'last_name', 'email', 'cargo', 'area', 'fecha_ingreso', 'is_active')
    search_fields = ('first_name', 'last_name', 'RUT', 'cargo', 'area')
    list_filter = ('sexo', 'cargo', 'area', 'is_active')
    ordering = ('first_name', 'sexo')  
    fieldsets = (
        ('Información Personal', {
            'fields': ('username', 'RUT', 'first_name', 'last_name', 'sexo', 'fecha_ingreso', 'email')
        }),
        ('Información Laboral', {
            'fields': ('cargo', 'area')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
    )

# Configuración para mostrar el modelo ContactoEmergencia
@admin.register(ContactoEmergencia)
class ContactoEmergenciaAdmin(admin.ModelAdmin):
    list_display = ('trabajador', 'nombre_contacto', 'relacion', 'telefono_contacto')
    search_fields = ('trabajador__first_name', 'trabajador__last_name', 'nombre_contacto')
    list_filter = ('relacion',)

# Configuración para mostrar el modelo CargaFamiliar
@admin.register(CargaFamiliar)
class CargaFamiliarAdmin(admin.ModelAdmin):
    list_display = ('trabajador', 'nombre_carga', 'parentesco', 'sexo', 'rut')
    search_fields = ('trabajador__first_name', 'trabajador__last_name', 'nombre_carga', 'rut')
    list_filter = ('sexo', 'parentesco')

# Configuración para mostrar el modelo Departamento en el admin
@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
