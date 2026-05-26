from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm


class formularioRegistroUsuario(UserCreationForm):
    pass

class perfilClienteform(forms.ModelForm):
    class Meta:
        model = cuenta
        fields = '__all__'
class muebleForm(forms.ModelForm):
    class Meta:
        model = mueble
        fields = '__all__'

class detalleCompraForm(forms.ModelForm):
    class Meta:
        model = detalleCompra
        fields = '__all__'