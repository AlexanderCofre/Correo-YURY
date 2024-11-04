from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Trabajador, ContactoEmergencia, CargaFamiliar

class TrabajadorRegistroForm(UserCreationForm):
    RUT = forms.CharField(max_length=12)
    first_name = forms.CharField(max_length=30, required=True) 
    last_name = forms.CharField(max_length=150, required=True)  
    email = forms.EmailField(required=True)                      
    sexo = forms.ChoiceField(choices=[('M', 'Masculino'), ('F', 'Femenino')])
    fecha_ingreso = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    cargo = forms.CharField(max_length=50)
    area = forms.CharField(max_length=50)

    class Meta:
        model = Trabajador
        fields = ['password1', 'password2', 'RUT', 'first_name', 'last_name', 'email', 'sexo', 'fecha_ingreso', 'cargo', 'area']
    
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

class TrabajadorLoginForm(AuthenticationForm):
    username = forms.CharField(label="RUT o nombre de usuario")
    password = forms.CharField(widget=forms.PasswordInput)

class TrabajadorUpdateForm(forms.ModelForm):
    class Meta:
        model = Trabajador
        fields = ['first_name', 'last_name', 'cargo', 'area']
