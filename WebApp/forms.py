from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Trabajador, Cargo, Area, Departamento

class TrabajadorRegistroForm(UserCreationForm):
    RUT = forms.CharField(max_length=12)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    sexo = forms.ChoiceField(choices=[('M', 'Masculino'), ('F', 'Femenino')])
    fecha_ingreso = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    departamento = forms.ModelChoiceField(
    queryset=Departamento.objects.all(), 
    required=True, 
    label="Departamento", 
    empty_label="Seleccione un departamento"
    )
    area = forms.ModelChoiceField(
        queryset=Area.objects.none(), 
        required=True, 
        label="Área", 
        empty_label=None
    )
    cargo = forms.ModelChoiceField(
        queryset=Cargo.objects.none(), 
        required=True, 
        label="Cargo", 
        empty_label=None
    )

    class Meta:
        model = Trabajador
        fields = [
            'password1', 'password2', 'RUT', 'first_name', 'last_name', 'email', 'sexo',
            'fecha_ingreso', 'departamento', 'area', 'cargo'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar el queryset de cargos según el área seleccionada
        if 'area' in self.data:
            try:
                area_id = int(self.data.get('area'))
                self.fields['cargo'].queryset = Cargo.objects.filter(area_id=area_id)
            except (ValueError, TypeError):
                self.fields['cargo'].queryset = Cargo.objects.none()
        elif self.instance.pk:
            self.fields['cargo'].queryset = self.instance.area.cargos.all()
        else:
            self.fields['cargo'].queryset = Cargo.objects.none()  # Ninguna opción por defecto

        # Asegúrate de que el área se configure correctamente también
        if 'departamento' in self.data:
            try:
                departamento_id = int(self.data.get('departamento'))
                self.fields['area'].queryset = Area.objects.filter(departamento_id=departamento_id)
            except (ValueError, TypeError):
                self.fields['area'].queryset = Area.objects.none()
        elif self.instance.pk:
            self.fields['area'].queryset = self.instance.departamento.areas.all()

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
