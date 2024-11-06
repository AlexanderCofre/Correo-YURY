from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import TrabajadorRegistroForm, TrabajadorLoginForm, TrabajadorUpdateForm, ContactoEmergenciaForm, CargaFamiliarForm, TrabajadorDetallesForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
            return redirect('login')
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
def listar_trabajadores(request):
    # Filtrar para obtener solo los trabajadores
    trabajadores = Trabajador.objects.filter(is_superuser=False)

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
    trabajador = Trabajador.objects.get(id=trabajador_id)

    if request.method == "POST":
        # Crear formularios con los datos del POST y la instancia del trabajador
        form_info = TrabajadorUpdateForm(request.POST, instance=trabajador)
        form_detalles = TrabajadorDetallesForm(request.POST, instance=trabajador)

        # Procesar primero el formulario de información básica
        if form_info.is_valid():
            form_info.save()
            # Si el formulario de información básica es válido, guardamos los cambios de este formulario
            form_info_saved = True
        else:
            form_info_saved = False
            print("Errores en form_info:", form_info.errors)

        # Procesar el formulario de detalles
        if form_detalles.is_valid():
            form_detalles.save()
            # Si el formulario de detalles es válido, guardamos los cambios de este formulario
            form_detalles_saved = True
        else:
            form_detalles_saved = False
            print("Errores en form_detalles:", form_detalles.errors)

        # Si ambos formularios son válidos, redirigimos
        if form_info_saved and form_detalles_saved:
            return redirect('cuenta')

    else:
        # Si no es un POST, pre-cargar los formularios con la instancia del trabajador
        form_info = TrabajadorUpdateForm(instance=trabajador)
        form_detalles = TrabajadorDetallesForm(instance=trabajador)

    context = {
        'form_info': form_info,
        'form_detalles': form_detalles
    }

    return render(request, 'actualizar_trabajador.html', context)

@login_required
def eliminar_trabajador(request, trabajador_id):
    trabajador = get_object_or_404(Trabajador, id=trabajador_id)

    # Eliminar al trabajador directamente
    trabajador.delete()
    messages.success(request, "El trabajador ha sido eliminado exitosamente.")
    
    # Redirigir a la lista de trabajadores o a la página deseada
    return redirect('trabajadores')  # Cambia 'trabajadores' por la URL deseada

def cargar_areas(request):
    departamento_id = request.GET.get('departamento_id')
    areas = Area.objects.filter(departamento_id=departamento_id)
    areas_data = [{'id': area.id, 'nombre': area.nombre} for area in areas]
    return JsonResponse(areas_data, safe=False)

def cargar_cargos(request):
    area_id = request.GET.get('area_id')
    cargos = Cargo.objects.filter(area_id=area_id)
    cargos_data = [{'id': cargo.id, 'nombre': cargo.nombre} for cargo in cargos]
    return JsonResponse(cargos_data, safe=False)

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
