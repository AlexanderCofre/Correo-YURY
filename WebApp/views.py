from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import TrabajadorRegistroForm, TrabajadorLoginForm, TrabajadorUpdateForm
from django.contrib.auth.decorators import login_required

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
