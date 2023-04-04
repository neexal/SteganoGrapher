from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control mb-4'}),
            'email': forms.EmailInput(attrs={'class': 'form-control mb-4'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control mb-4'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control mb-4'}),
        }