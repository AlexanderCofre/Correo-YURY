from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import TrabajadorRegistroForm, TrabajadorLoginForm, TrabajadorUpdateForm, ContactoEmergenciaForm, CargaFamiliarForm, TrabajadorDetallesForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Trabajador, Cargo, Area, Departamento, CargaFamiliar, ContactoEmergencia
from django.http import Http404, JsonResponse

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
    try:
        trabajador = Trabajador.objects.get(id=trabajador_id)
    except Trabajador.DoesNotExist:
        return redirect('trabajadores')  # Redirige si el trabajador no existe

    if request.method == "POST":
        # Usar la instancia del trabajador para editar
        form_info = TrabajadorUpdateForm(request.POST, instance=trabajador)
        form_detalles = TrabajadorDetallesForm(request.POST, instance=trabajador)

        # Validar y guardar el formulario de información básica
        if form_info.is_valid():
            form_info.save()
        else:
            form_info_saved = False
            print("Errores en form_info:", form_info.errors)

        # Validar y guardar el formulario de detalles
        if form_detalles.is_valid():
            form_detalles.save()
        else:
            form_detalles_saved = False
            print("Errores en form_detalles:", form_detalles.errors)

        # Redirigir solo si ambos formularios son válidos
        if form_info.is_valid() and form_detalles.is_valid():
            return redirect('trabajadores')  # Redirige al listado de trabajadores

    else:
        form_info = TrabajadorUpdateForm(instance=trabajador)
        form_detalles = TrabajadorDetallesForm(instance=trabajador)

    context = {
        'form_info': form_info,
        'form_detalles': form_detalles,
        'trabajador_id': trabajador_id,  # Pasar el ID de trabajador al template
    }

    return render(request, 'actualizar_trabajador.html', context)


@login_required
def eliminar_cuenta(request, trabajador_id):
    # Asegurarse de que el trabajador que está intentando eliminar su cuenta es el mismo que está logueado
    if request.user.id == trabajador_id:
        try:
            trabajador = Trabajador.objects.get(id=trabajador_id)
            trabajador.delete()
            messages.success(request, "Tu cuenta ha sido eliminada con éxito.")
            return redirect('login')  # Redirigir a la página de login
        except Trabajador.DoesNotExist:
            raise Http404("El trabajador no existe.")
    else:
        messages.error(request, "No tienes permisos para eliminar esta cuenta.")
        return redirect('inicio')  # O redirigir a la página que prefieras

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

@login_required
def editar_carga_familiar(request, carga_id=None):
    # Aquí ya no necesitas acceder a un campo `trabajador` porque `request.user` es el modelo Trabajador
    trabajador = request.user

    # Si existe carga_familiar, obtenla, si no, crear un nuevo objeto vacío
    if carga_id:
        carga = get_object_or_404(CargaFamiliar, id=carga_id, trabajador=trabajador)
    else:
        carga = None

    if request.method == 'POST':
        form = CargaFamiliarForm(request.POST, instance=carga)
        if form.is_valid():
            carga_familiar = form.save(commit=False)
            carga_familiar.trabajador = trabajador  # Asocia la carga con el trabajador actual
            carga_familiar.save()
            return redirect('cuenta')  # Redirige a la página de cuenta después de guardar
    else:
        form = CargaFamiliarForm(instance=carga)

    return render(request, 'editar_carga_familiar.html', {'form': form})

@login_required
def agregar_carga_familiar(request):
    trabajador = request.user  # Obtener el trabajador vinculado al usuario

    if request.method == 'POST':
        form = CargaFamiliarForm(request.POST)
        if form.is_valid():
            nueva_carga = form.save(commit=False)
            nueva_carga.trabajador = trabajador  # Asociar la carga con el trabajador actual
            nueva_carga.save()
            return redirect('cuenta')  # Redirigir a la página "Cuenta" o donde necesites
    else:
        form = CargaFamiliarForm()
    
    return render(request, 'agregar_carga_familiar.html', {'form': form})

@login_required
def agregar_contacto_emergencia(request):
    try:
        trabajador = request.user  # Obtener el trabajador vinculado al usuario
    except Trabajador.DoesNotExist:
        # Si no existe el trabajador asociado, puedes redirigir o mostrar un mensaje de error
        return redirect('error')  # O cualquier otra página para manejar el error
    
    if request.method == 'POST':
        # Crear un formulario con los datos del POST
        form = ContactoEmergenciaForm(request.POST)
        if form.is_valid():
            # Guardamos el formulario, asociando el contacto al trabajador
            contacto_emergencia = form.save(commit=False)
            contacto_emergencia.trabajador = trabajador  # Asocia el contacto con el trabajador actual
            contacto_emergencia.save()  # Guardamos el contacto
            return redirect('cuenta')  # Redirige a la cuenta o a donde desees
    else:
        form = ContactoEmergenciaForm()  # Formulario vacío para la vista GET
    
    return render(request, 'agregar_contacto_emergencia.html', {'form': form})

@login_required
def editar_contacto_emergencia(request, contacto_id):
    # Obtener el contacto de emergencia asociado al trabajador actual
    contacto = get_object_or_404(ContactoEmergencia, id=contacto_id, trabajador=request.user)

    if request.method == 'POST':
        form = ContactoEmergenciaForm(request.POST, instance=contacto)
        if form.is_valid():
            form.save()  # Guardamos el formulario
            return redirect('cuenta')  # O donde necesites redirigir
    else:
        form = ContactoEmergenciaForm(instance=contacto)
    
    return render(request, 'editar_contacto_emergencia.html', {'form': form, 'contacto': contacto})