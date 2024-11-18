"""
URL configuration for CorreoYury project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from WebApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path('register/', views.registro_trabajador, name='registro'),
    path('login/', views.login_trabajador, name='login'),
    path('logout/', views.logout_trabajador, name='logout'),

    # Rutas para la recuperacion de contraseña
    path('recuperar_contraseña/', views.recuperar_contraseña, name='recuperar_contraseña'),
    path('reiniciar_contraseña/<str:token>/', views.reiniciar_contraseña, name='reiniciar_contraseña'),

    # Rutas del ADMINISTRADOR
    path('trabajadores/', views.listar_trabajadores, name='trabajadores'),
    path('trabajador/<int:trabajador_id>/', views.ver_trabajador, name='ver_trabajador'),
    path('trabajador/<int:trabajador_id>/actualizar/', views.actualizar_datos_trabajador, name='actualizar_datos_trabajador'),
    path('trabajador/<int:trabajador_id>/editar-informacion-empleo/', views.editar_informacion_empleo, name='editar_informacion_empleo'),
    path('trabajadores/<int:trabajador_id>/agregar_informacion_empleo/', views.agregar_informacion_empleo, name='agregar_informacion_empleo'),
    path('trabajador/<int:trabajador_id>/agregar-carga-familiar/', views.agregar_carga_familiarAdmin, name='agregar_carga_familiar_admin'),
    path('trabajador/<int:trabajador_id>/carga/<int:carga_id>/editar/', views.editar_carga_familiarAdmin, name='editar_carga_familiar_admin'),
    path('trabajador/<int:trabajador_id>/agregar-contacto-emergencia/', views.agregar_contacto_emergenciaAdmin, name='agregar_contacto_emergencia_admin'),
    path('trabajador/<int:trabajador_id>/contacto/<int:contacto_id>/editar/', views.editar_contacto_emergenciaAdmin, name='editar_contacto_emergencia_admin'),

    # Rutas del TRABAJADOR
    path('mi-cuenta/eliminar/<int:trabajador_id>/', views.eliminar_cuenta, name='eliminar_cuenta'),
    path("cargar-areas/", views.cargar_areas, name="cargar_areas"),
    path("cargar_cargos/", views.cargar_cargos, name="cargar_cargos"),
    path('mi-cuenta/', views.mi_cuenta, name='cuenta'),
    path('agregar_carga_familiar/', views.agregar_carga_familiar, name='agregar_carga_familiar'),
    path('carga_familiar/<int:carga_id>/', views.editar_carga_familiar, name='editar_carga_familiar'),
    path('contacto_emergencia/agregar/', views.agregar_contacto_emergencia, name='agregar_contacto_emergencia'),
    path('contacto_emergencia/editar/<int:contacto_id>/', views.editar_contacto_emergencia, name='editar_contacto_emergencia'),
]
