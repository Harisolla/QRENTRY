# events/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Username', max_length=30)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        fields = ('username', 'password')