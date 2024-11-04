from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import TrabajadorRegistroForm, TrabajadorLoginForm, TrabajadorUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Trabajador

def inicio(request):
    return render(request, 'index.html')

def registro_trabajador(request):
    if request.method == "POST":
        form = TrabajadorRegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            # Agrega esta línea para ver errores en la consola
            print(form.errors)
    else:
        form = TrabajadorRegistroForm()
    return render(request, 'registro.html', {'form': form})


def login_trabajador(request):
    if request.method == "POST":
        form = TrabajadorLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            trabajador = authenticate(username=username, password=password)
            if trabajador is not None:
                login(request, trabajador)
                return redirect('inicio')  # Redirigir a la página principal
    else:
        form = TrabajadorLoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def logout_trabajador(request):
    logout(request)
    return redirect('login')  # Redirigir al formulario de inicio de sesión

@login_required
def actualizar_trabajador(request):
    if request.method == "POST":
        form = TrabajadorUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirigir a la página de perfil del trabajador
    else:
        form = TrabajadorUpdateForm(instance=request.user)
    return render(request, 'actualizar.html', {'form': form})

@login_required
def listar_trabajadores(request):
    trabajadores = Trabajador.objects.all()  # Recupera todos los trabajadores de la base de datos
    return render(request, 'trabajadores.html', {'trabajadores': trabajadores})

@login_required
def actualizar_trabajador(request, trabajador_id):
    trabajador = get_object_or_404(Trabajador, id=trabajador_id)
    
    if request.method == 'POST':
        form = TrabajadorUpdateForm(request.POST, instance=trabajador)
        if form.is_valid():
            form.save()
            return redirect('trabajadores')  # Redirige a la lista de trabajadores después de actualizar
    else:
        form = TrabajadorUpdateForm(instance=trabajador)

    return render(request, 'actualizar_trabajador.html', {'form': form, 'trabajador': trabajador})

@login_required
def eliminar_trabajador(request, trabajador_id):
    trabajador = get_object_or_404(Trabajador, id=trabajador_id)
    
    if request.method == 'POST':
        trabajador.delete()
        messages.success(request, "Tu cuenta ha sido eliminada exitosamente.")
        return redirect('login')  # Redirige al login o a la página de inicio

    return render(request, 'eliminar_trabajador_confirmacion.html', {'trabajador': trabajador})