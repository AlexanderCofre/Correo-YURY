from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import TrabajadorRegistroForm, TrabajadorLoginForm, TrabajadorUpdateForm, ContactoEmergenciaForm, CargaFamiliarForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import formset_factory
from .models import Trabajador, Cargo, Area, Departamento
from django.http import JsonResponse

def inicio(request):
    return render(request, 'index.html')

def registro_trabajador(request):
    if request.method == 'POST':
        trabajador_form = TrabajadorRegistroForm(request.POST)
        
        if trabajador_form.is_valid():
            trabajador_form.save()
            messages.success(request, "Registro exitoso")
            return redirect('inicio')
        else:
            messages.error(request, "Por favor, corrija los errores en el formulario.")

    else:
        trabajador_form = TrabajadorRegistroForm()

    context = {
        'trabajador_form': trabajador_form
    }
    return render(request, 'registro.html', context)


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

@login_required
def mi_cuenta(request):
    trabajador = Trabajador.objects.get(id=request.user.id)  # Obtenemos el trabajador actual
    carga_form = CargaFamiliarForm()
    contacto_form = ContactoEmergenciaForm()

    # Si el formulario de Carga Familiar es enviado
    if request.method == 'POST':
        if 'carga_familiar' in request.POST:  # Identificamos que se envió el formulario de carga familiar
            carga_form = CargaFamiliarForm(request.POST)
            if carga_form.is_valid():
                carga_form.save(trabajador=trabajador)  # Pasamos el trabajador al formulario

        # Si el formulario de Contacto de Emergencia es enviado
        elif 'contacto_emergencia' in request.POST:  # Identificamos que se envió el formulario de contacto de emergencia
            contacto_form = ContactoEmergenciaForm(request.POST)
            if contacto_form.is_valid():
                contacto_form.save(trabajador=trabajador)  # Pasamos el trabajador al formulario

    return render(request, 'mi_cuenta.html', {
        'trabajador': trabajador, 
        'carga_form': carga_form,
        'contacto_form': contacto_form
    })
