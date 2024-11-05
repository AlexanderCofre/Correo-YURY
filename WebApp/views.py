from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import TrabajadorRegistroForm, TrabajadorLoginForm, TrabajadorUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Trabajador, Cargo, Area, Departamento
from django.http import JsonResponse

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

from django.db.models import Q

@login_required
def listar_trabajadores(request):
    trabajadores = Trabajador.objects.all()
    sexo = request.GET.get('sexo')
    cargo_id = request.GET.get('cargo')
    area_id = request.GET.get('area')
    departamento_id = request.GET.get('departamento')

    # Aplicar filtros si los valores están presentes
    if sexo:
        trabajadores = trabajadores.filter(sexo=sexo)
    if cargo_id:
        trabajadores = trabajadores.filter(cargo_id=cargo_id)
    if area_id:
        trabajadores = trabajadores.filter(area_id=area_id)
    if departamento_id:
        trabajadores = trabajadores.filter(area__departamento_id=departamento_id)

    context = {
        'trabajadores': trabajadores,
        'sexos': [('M', 'Masculino'), ('F', 'Femenino')],
        'cargos': Cargo.objects.all(),
        'areas': Area.objects.all(),
        'departamentos': Departamento.objects.all(),
        'selected_sexo': sexo,
        'selected_cargo': cargo_id,
        'selected_area': area_id,
        'selected_departamento': departamento_id,
    }
    return render(request, 'trabajadores.html', context)

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

def cargar_areas(request):
    departamento_id = request.GET.get("departamento_id")
    areas = Area.objects.filter(departamento_id=departamento_id).values("id", "nombre")
    return JsonResponse(list(areas), safe=False)

def cargar_cargos(request):
    area_id = request.GET.get("area_id")
    cargos = Cargo.objects.filter(area_id=area_id).values("id", "nombre")
    return JsonResponse(list(cargos), safe=False)