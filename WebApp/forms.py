from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Trabajador, Cargo, Area, Departamento, ContactoEmergencia, CargaFamiliar
from django.core.exceptions import ValidationError
import re

class TrabajadorRegistroForm(UserCreationForm):
    RUT = forms.CharField(max_length=12)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    sexo = forms.ChoiceField(choices=[('M', 'Masculino'), ('F', 'Femenino')])

    class Meta:
        model = Trabajador
        fields = [
            'password1', 'password2', 'RUT', 'first_name', 'last_name', 'email', 'sexo'
        ]

    def save(self, commit=True):
        trabajador = super().save(commit=False)

        # Generar el username utilizando el último dígito del RUT
        if self.cleaned_data['RUT']:
            last_digit = self.cleaned_data['RUT'][-1]  # Obtiene el último dígito del RUT
            username = f"{self.cleaned_data['first_name'][0].lower()}{self.cleaned_data['last_name'].lower()}{last_digit}"
            trabajador.username = username

        if commit:
            trabajador.save()
        return trabajador

    def clean_RUT(self):
        rut = self.cleaned_data.get('RUT')
        if not self.validar_rut(rut):
            raise forms.ValidationError('El RUT ingresado no es válido.')
        return rut

    def validar_rut(self, rut):
        # Eliminar espacios y guiones
        rut = rut.replace(" ", "").replace("-", "")
        
        # Validar formato
        if len(rut) < 2 or not rut[:-1].isdigit() or not (rut[-1].isdigit() or rut[-1].upper() == 'K'):
            return False

        # Separar el número y el dígito verificador
        numero = int(rut[:-1])
        digito_verificador = rut[-1].upper()
        
        # Calcular el dígito verificador
        suma = 0
        multiplicador = 2

        for i in reversed(str(numero)):
            suma += int(i) * multiplicador
            multiplicador = 2 if multiplicador == 7 else multiplicador + 1

        digito_calculado = 11 - (suma % 11)
        if digito_calculado == 11:
            digito_calculado = '0'
        elif digito_calculado == 10:
            digito_calculado = 'K'
        else:
            digito_calculado = str(digito_calculado)
        
        # Comparar el dígito calculado con el dígito verificador
        return digito_calculado == digito_verificador


class TrabajadorLoginForm(AuthenticationForm):
    username = forms.CharField(label="RUT o nombre de usuario")
    password = forms.CharField(widget=forms.PasswordInput)


class TrabajadorUpdateForm(forms.ModelForm):
    class Meta:
        model = Trabajador
        fields = ['first_name', 'last_name', 'email', 'sexo']  # Campos editables por el usuario

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-control'}),
        }

# Función para validar teléfono chileno
def validar_telefono_chileno(value):
    if not re.match(r"^\+56\s?9?\d{8}$", value):
        raise ValidationError("El teléfono debe ser un número chileno válido (+56 9XXXXXXXX).")

# Formulario para ContactoEmergencia
class ContactoEmergenciaForm(forms.ModelForm):
    telefono_contacto = forms.CharField(
        max_length=15,
        validators=[validar_telefono_chileno],
        label="Teléfono de Contacto"
    )

    class Meta:
        model = ContactoEmergencia
        fields = ['nombre_contacto', 'apellido_contacto', 'relacion', 'telefono_contacto']
        labels = {
            'nombre_contacto': 'Nombre del Contacto',
            'apellido_contacto': 'Apellido del Contacto',
            'relacion': 'Relación con el Trabajador'
        }

    # Modificación para asociar el trabajador automáticamente
    def save(self, commit=True, trabajador=None):
        if trabajador:
            self.instance.trabajador = trabajador
        return super().save(commit=commit)

# Formulario para CargaFamiliar
class CargaFamiliarForm(forms.ModelForm):
    rut = forms.CharField(validators=[], label="RUT")
    sexo = forms.ChoiceField(choices=[('M', 'Masculino'), ('F', 'Femenino')])

    class Meta:
        model = CargaFamiliar
        fields = ['nombre_carga', 'parentesco', 'sexo', 'rut']
        labels = {
            'nombre_carga': 'Nombre de la Carga Familiar',
            'parentesco': 'Parentesco',
            'sexo': 'Sexo'
        }

    def save(self, commit=True, trabajador=None):
        # Asignar el trabajador actual al campo trabajador
        if trabajador:
            self.instance.trabajador = trabajador
        return super().save(commit=commit)

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if not self.validar_rut(rut):
            raise forms.ValidationError('El RUT ingresado no es válido.')
        return rut

    def validar_rut(self, rut):
        # Eliminar espacios y guiones
        rut = rut.replace(" ", "").replace("-", "")
        
        # Validar formato
        if len(rut) < 2 or not rut[:-1].isdigit() or not (rut[-1].isdigit() or rut[-1].upper() == 'K'):
            return False

        # Separar el número y el dígito verificador
        numero = int(rut[:-1])
        digito_verificador = rut[-1].upper()
        
        # Calcular el dígito verificador
        suma = 0
        multiplicador = 2

        for i in reversed(str(numero)):
            suma += int(i) * multiplicador
            multiplicador = 2 if multiplicador == 7 else multiplicador + 1

        digito_calculado = 11 - (suma % 11)
        if digito_calculado == 11:
            digito_calculado = '0'
        elif digito_calculado == 10:
            digito_calculado = 'K'
        else:
            digito_calculado = str(digito_calculado)
        
        # Comparar el dígito calculado con el dígito verificador
        return digito_calculado == digito_verificador
