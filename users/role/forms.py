# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PermisoProducto

class SignUpForm(UserCreationForm):
    puede_agregar = forms.BooleanField(label='¿Puede agregar productos?', required=False)
    puede_cambiar = forms.BooleanField(label='¿Puede cambiar productos?', required=False)
    puede_eliminar = forms.BooleanField(label='¿Puede eliminar productos?', required=False)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'puede_agregar', 'puede_cambiar', 'puede_eliminar')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            permisos = PermisoProducto.objects.create(
                user=user,
                puede_agregar=self.cleaned_data.get('puede_agregar', False),
                puede_cambiar=self.cleaned_data.get('puede_cambiar', False),
                puede_eliminar=self.cleaned_data.get('puede_eliminar', False),
            )
        return user
