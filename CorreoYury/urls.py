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
    path('trabajadores/', views.listar_trabajadores, name='trabajadores'),
    path('trabajador/<int:trabajador_id>/', views.ver_trabajador, name='ver_trabajador'),
    path('trabajador/<int:trabajador_id>/actualizar/', views.actualizar_datos_trabajador, name='actualizar_datos_trabajador'),
    path('mi-cuenta/eliminar/<int:trabajador_id>/', views.eliminar_cuenta, name='eliminar_cuenta'),
    path("cargar-areas/", views.cargar_areas, name="cargar_areas"),
    path("cargar_cargos/", views.cargar_cargos, name="cargar_cargos"),
    path('mi-cuenta/', views.mi_cuenta, name='cuenta'),
    path('agregar_carga_familiar/', views.agregar_carga_familiar, name='agregar_carga_familiar'),
    path('carga_familiar/<int:carga_id>/', views.editar_carga_familiar, name='editar_carga_familiar'),
    path('contacto_emergencia/agregar/', views.agregar_contacto_emergencia, name='agregar_contacto_emergencia'),
    path('contacto_emergencia/editar/<int:contacto_id>/', views.editar_contacto_emergencia, name='editar_contacto_emergencia'),
]
