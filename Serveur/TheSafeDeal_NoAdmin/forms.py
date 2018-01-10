from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=100, help_text='Required', widget=forms.TextInput(attrs={'placeholder': 'Entrer Email'}))
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2','typeUser')
        labels = {
        	"typeUser": "Vous êtes un :"
        }
        widgets = {
        	'Password' : forms.PasswordInput(attrs = {'placeholder': 'Entrer Mot de Passe'}),
            'username' : forms.TextInput(attrs = {'placeholder': 'Entrer Username'}),
            'password2' : forms.PasswordInput(attrs = {'placeholder': 'Répéter Mot de Passe'}),}