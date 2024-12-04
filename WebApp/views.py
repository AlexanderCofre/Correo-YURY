from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import TrabajadorRegistroForm, TrabajadorLoginForm, ContactoEmergenciaForm, CargaFamiliarForm, TrabajadorUpdateFormAdmin, RecuperarContraseñaForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.core.mail import send_mail
from .models import Trabajador, Cargo, Area, Departamento, CargaFamiliar, ContactoEmergencia
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.conf import settings
from django.http import Http404, JsonResponse
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import json
import re


def inicio(request):
    return render(request, 'index.html')


def registro_trabajador(request):
    if request.method == 'POST':
        trabajador_form = TrabajadorRegistroForm(request.POST)
        
        if trabajador_form.is_valid():
            trabajador = trabajador_form.save()
            messages.success(request, "Registro exitoso")

            # Generar URL absoluta para "login"
            login_url = request.build_absolute_uri(reverse('login'))

            # Datos del correo
            subject = 'Bienvenido a nuestro sistema'
            html_message = render_to_string(
                'correos/bienvenida.html',  # Ruta a la plantilla HTML
                {
                    'trabajador': trabajador, 
                    'login_url': login_url  # Pasar la URL al template
                }
            )
            plain_message = strip_tags(html_message)  # Texto sin formato como respaldo
            recipient_list = [trabajador.email]

            # Enviar el correo
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                html_message=html_message,  # Enviar versión HTML
                fail_silently=False,
            )

            return redirect('login')
        else:
            messages.error(request, "Por favor, corrija los errores en el formulario.")
    else:
        trabajador_form = TrabajadorRegistroForm()

    context = {
        'trabajador_form': trabajador_form
    }
    return render(request, 'trabajador/registro.html', context)


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


def soporte(request):
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion', '').strip()  # Capturar el problema ingresado
        if descripcion:
            usuario = request.user  # Asumimos que el usuario está autenticado

            # Datos del correo
            subject = f'Problema reportado por {usuario.get_full_name()} ({usuario.RUT})'
            message = f"""
            Se ha recibido un nuevo problema.

            Usuario: {usuario.get_full_name()} (RUT: {usuario.RUT})
            Email: {usuario.email}

            Descripción del problema:
            {descripcion}
            """
            # recipient_list = ['soporte@correo.com']  # Dirección de soporte
            recipient_list = ['brioneselias2024@gmail.com']

            # Enviar el correo
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    recipient_list,
                    fail_silently=False,
                )
                messages.success(request, "Tu problema ha sido enviado exitosamente.")
            except Exception as e:
                messages.error(request, "Ocurrió un error al enviar tu problema. Inténtalo nuevamente.")
        else:
            messages.error(request, "Por favor, describe el problema antes de enviarlo.")

    return render(request, 'soporte.html')


# Lógica para reiniciar la contraseña
signer = TimestampSigner()

def recuperar_contraseña(request):
    if request.method == 'POST':
        form = RecuperarContraseñaForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                trabajador = Trabajador.objects.get(email=email)
                
                # Generar el token y URL de restablecimiento
                token = signer.sign(trabajador.username)
                reset_url = request.build_absolute_uri(f"/reiniciar_contraseña/{token}/")
                
                # Contexto para el correo
                context = {
                    'trabajador': trabajador,
                    'reset_url': reset_url,
                }
                
                # Plantilla del correo
                message = render_to_string('correos/recuperar_contraseña.html', context)
                
                # Enviar el correo
                send_mail(
                    "Recuperación de contraseña",
                    None,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                    html_message=message  # Asegúrate de usar html_message
                )

                messages.success(request, "Se ha enviado un correo con las instrucciones.")
                return redirect('recuperar_contraseña')
            except Trabajador.DoesNotExist:
                messages.error(request, 'No existe un usuario con este correo.')
    else:
        form = RecuperarContraseñaForm()
    return render(request, 'recuperar_contraseña.html', {'form': form})


def reiniciar_contraseña(request, token):
    try:
        # Validar el token
        username = signer.unsign(token, max_age=3600)  # Token válido por 1 hora
        user = Trabajador.objects.get(username=username)
    except (BadSignature, SignatureExpired, Trabajador.DoesNotExist):
        messages.error(request, 'El enlace no es válido o ha expirado.')
        return redirect('recuperar_contraseña')

    if request.method == 'POST':
        nueva_contraseña = request.POST.get('password')
        confirmar_contraseña = request.POST.get('password_confirm')

        # Depuración de valores
        print(f"Contraseña ingresada: {nueva_contraseña}")
        print(f"Confirmar contraseña: {confirmar_contraseña}")

        # Definir el patrón para validar la contraseña
        contraseña_valida = re.compile(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_])[A-Za-z\d@$!%*?&_]{8,}$'
        )

        if nueva_contraseña and nueva_contraseña == confirmar_contraseña:
            if not contraseña_valida.match(nueva_contraseña):
                print("Contraseña no cumple con los requisitos.")  # Depuración
                messages.error(
                    request,
                    'La contraseña debe tener al menos 8 caracteres, incluir mayúsculas, minúsculas, números y un símbolo.'
                )
            else:
                print("Contraseña válida.")  # Depuración
                # Guardar la nueva contraseña
                user.password = make_password(nueva_contraseña)
                user.save()
                messages.success(request, 'Contraseña actualizada exitosamente.')
                return redirect('login')
        else:
            messages.error(request, 'Las contraseñas no coinciden.')

    return render(request, 'reiniciar_contraseña.html', {'token': token})


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
    return render(request, 'admin/trabajadores.html', context)


@login_required
def ver_trabajador(request, trabajador_id):
    trabajador = get_object_or_404(Trabajador, id=trabajador_id)
    return render(request, 'admin/ver_trabajador.html', {'trabajador': trabajador})


@login_required
def agregar_informacion_empleo(request, trabajador_id):
    trabajador = get_object_or_404(Trabajador, id=trabajador_id)
    departamentos = Departamento.objects.all()
    areas = Area.objects.all()
    cargos = Cargo.objects.all()

    if request.method == 'POST':
        departamento_id = request.POST.get('departamento')
        area_id = request.POST.get('area')
        cargo_id = request.POST.get('cargo')
        fecha_ingreso = request.POST.get('fecha_ingreso')

        trabajador.departamento_id = departamento_id
        trabajador.area_id = area_id
        trabajador.cargo_id = cargo_id
        trabajador.fecha_ingreso = fecha_ingreso  # Asignar la fecha de ingreso
        trabajador.save()
        return redirect('ver_trabajador', trabajador.id)

    return render(request, 'admin/agregar_informacion_empleo.html', {
        'trabajador': trabajador,
        'departamentos': departamentos,
        'departamentos_json': json.dumps(list(departamentos.values('id', 'nombre'))),
        'areas_json': json.dumps(list(areas.values('id', 'nombre', 'departamento_id'))),
        'cargos_json': json.dumps(list(cargos.values('id', 'nombre', 'area_id'))),
    })



@login_required
def actualizar_datos_trabajador(request, trabajador_id):
    trabajador = get_object_or_404(Trabajador, id=trabajador_id)
    if request.method == 'POST':
        form = TrabajadorUpdateFormAdmin(request.POST, instance=trabajador)
        if form.is_valid():
            form.save()
            messages.success(request, 'Los datos personales han sido actualizados con éxito.')
            return redirect('ver_trabajador', trabajador_id=trabajador_id)
    else:
        form = TrabajadorUpdateFormAdmin(instance=trabajador)
    
    return render(request, 'admin/actualizar_datos_trabajador.html', {'form': form, 'trabajador': trabajador})


@login_required
def editar_informacion_empleo(request, trabajador_id):
    trabajador = get_object_or_404(Trabajador, id=trabajador_id)
    departamentos = Departamento.objects.all()
    areas = Area.objects.all()
    cargos = Cargo.objects.all()

    if request.method == 'POST':
        departamento_id = request.POST.get('departamento')
        area_id = request.POST.get('area')
        cargo_id = request.POST.get('cargo')
        fecha_ingreso = request.POST.get('fecha_ingreso')

        # Actualizar los campos
        trabajador.departamento_id = departamento_id
        trabajador.area_id = area_id
        trabajador.cargo_id = cargo_id
        trabajador.fecha_ingreso = fecha_ingreso
        trabajador.save()
        
        messages.success(request, 'Información actualizada correctamente.')
        return redirect('ver_trabajador', trabajador.id)

    return render(request, 'admin/actualizar_informacion_empleo.html', {
        'trabajador': trabajador,
        'departamentos': departamentos,
        'departamentos_json': json.dumps(list(departamentos.values('id', 'nombre'))),
        'areas_json': json.dumps(list(areas.values('id', 'nombre', 'departamento_id'))),
        'cargos_json': json.dumps(list(cargos.values('id', 'nombre', 'area_id'))),
    })

@login_required
def agregar_carga_familiarAdmin(request, trabajador_id):
    trabajador = get_object_or_404(Trabajador, id=trabajador_id)
    
    if request.method == 'POST':
        nombre_carga = request.POST.get('nombre_carga')
        parentesco = request.POST.get('parentesco')
        sexo = request.POST.get('sexo')
        rut = request.POST.get('rut')
        
        # Validaciones básicas
        if not all([nombre_carga, parentesco, sexo, rut]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('agregar_carga_familiar_admin', trabajador_id=trabajador.id)
        
        try:
            # Crear la carga familiar
            CargaFamiliar.objects.create(
                trabajador=trabajador,
                nombre_carga=nombre_carga,
                parentesco=parentesco,
                sexo=sexo,
                rut=rut
            )
            
            messages.success(request, 'Carga familiar agregada correctamente.')
            return redirect('ver_trabajador', trabajador.id)
            
        except Exception as e:
            messages.error(request, 'Error al agregar la carga familiar.')
            return redirect('agregar_carga_familiar', trabajador_id=trabajador.id)
    
    return render(request, 'admin/agregar_carga_familiar_admin.html', {
        'trabajador': trabajador,
    })


@login_required
def editar_carga_familiarAdmin(request, trabajador_id, carga_id):
    trabajador = get_object_or_404(Trabajador, id=trabajador_id)
    carga = get_object_or_404(CargaFamiliar, id=carga_id, trabajador=trabajador)

    if request.method == 'POST':
        nombre_carga = request.POST.get('nombre_carga')
        parentesco = request.POST.get('parentesco')
        sexo = request.POST.get('sexo')
        rut = request.POST.get('rut')

        # Validaciones básicas
        if not all([nombre_carga, parentesco, sexo, rut]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('editar_carga_familiar_admin', trabajador_id=trabajador.id, carga_id=carga.id)

        try:
            # Actualizar la carga familiar
            carga.nombre_carga = nombre_carga
            carga.parentesco = parentesco
            carga.sexo = sexo
            carga.rut = rut
            carga.save()

            messages.success(request, 'Carga familiar actualizada correctamente.')
            return redirect('ver_trabajador', trabajador.id)

        except Exception as e:
            messages.error(request, 'Error al actualizar la carga familiar.')
            return redirect('editar_carga_familiar_admin', trabajador_id=trabajador.id, carga_id=carga.id)

    return render(request, 'admin/editar_carga_familiar_admin.html', {
        'trabajador': trabajador,
        'carga': carga,
    })


@login_required
def agregar_contacto_emergenciaAdmin(request, trabajador_id):
    trabajador = get_object_or_404(Trabajador, id=trabajador_id)

    if request.method == 'POST':
        nombre_contacto = request.POST.get('nombre_contacto')
        apellido_contacto = request.POST.get('apellido_contacto')
        relacion = request.POST.get('relacion')
        telefono_contacto = request.POST.get('telefono_contacto')

        # Basic validation for required fields
        if not all([nombre_contacto, apellido_contacto, relacion, telefono_contacto]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('agregar_contacto_emergencia', trabajador_id=trabajador.id)

        try:
            # Create the emergency contact
            ContactoEmergencia.objects.create(
                trabajador=trabajador,
                nombre_contacto=nombre_contacto,
                apellido_contacto=apellido_contacto,
                relacion=relacion,
                telefono_contacto=telefono_contacto
            )

            messages.success(request, 'Contacto de emergencia agregado correctamente.')
            return redirect('ver_trabajador', trabajador.id)

        except Exception:
            messages.error(request, 'Error al agregar el contacto de emergencia. \n')
            return redirect('agregar_contacto_emergencia', trabajador_id=trabajador.id)

    return render(request, 'admin/agregar_contacto_emergencia_admin.html', {
        'trabajador': trabajador,
    })


@login_required
def editar_contacto_emergenciaAdmin(request, trabajador_id, contacto_id):
    trabajador = get_object_or_404(Trabajador, id=trabajador_id)
    contacto = get_object_or_404(ContactoEmergencia, id=contacto_id, trabajador=trabajador)

    if request.method == 'POST':
        nombre_contacto = request.POST.get('nombre_contacto')
        apellido_contacto = request.POST.get('apellido_contacto')
        relacion = request.POST.get('relacion')
        telefono_contacto = request.POST.get('telefono_contacto')

        # Basic validation for required fields
        if not all([nombre_contacto, apellido_contacto, relacion, telefono_contacto]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('editar_contacto_emergencia', trabajador_id=trabajador.id, contacto_id=contacto.id)

        try:
            # Update the emergency contact
            contacto.nombre_contacto = nombre_contacto
            contacto.apellido_contacto = apellido_contacto
            contacto.relacion = relacion
            contacto.telefono_contacto = telefono_contacto
            contacto.save()

            messages.success(request, 'Contacto de emergencia actualizado correctamente.')
            return redirect('ver_trabajador', trabajador.id)

        except Exception as e:
            messages.error(request, 'Error al actualizar el contacto de emergencia.')
            return redirect('editar_contacto_emergencia', trabajador_id=trabajador.id, contacto_id=contacto.id)

    return render(request, 'admin/editar_contacto_emergencia_admin.html', {
        'trabajador': trabajador,
        'contacto': contacto,
    })


@login_required
def eliminar_trabajador(request, trabajador_id):
    try:
        trabajador = Trabajador.objects.get(id=trabajador_id)
        trabajador.delete()
        messages.success(request, "El trabajador ha sido eliminado exitosamente.")
    except Trabajador.DoesNotExist:
        messages.error(request, "El trabajador no existe.")
    return redirect('trabajadores')  # Redirigir a la lista de trabajadores


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

    return render(request, 'trabajador/mi_cuenta.html', {
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

    return render(request, 'trabajador/editar_carga_familiar.html', {'form': form})


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
    
    return render(request, 'trabajador/agregar_carga_familiar.html', {'form': form})


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
    
    return render(request, 'trabajador/agregar_contacto_emergencia.html', {'form': form})


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
    
    return render(request, 'trabajador/editar_contacto_emergencia.html', {'form': form, 'contacto': contacto})
