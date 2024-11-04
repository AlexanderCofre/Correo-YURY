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
    path('trabajadores/actualizar/<int:trabajador_id>/', views.actualizar_trabajador, name='actualizar_trabajador'),
    path('trabajadores/eliminar/<int:trabajador_id>/', views.eliminar_trabajador, name='eliminar_trabajador'),
]
