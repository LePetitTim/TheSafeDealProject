from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Projet


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=100, help_text='Required', widget=forms.TextInput(attrs={'placeholder': 'Entrer Email'}))
    type = forms.ChoiceField(choices=(('Prestataire', 'Prestataire'),('Professionnel', 'Professionnel'),('Client', 'Client')),label='Vous êtes un :')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2','type')
        widgets = {
        	'Password' : forms.PasswordInput(attrs = {'placeholder': 'Entrer Mot de Passe'}),
            'username' : forms.TextInput(attrs = {'placeholder': 'Entrer Username'}),
            'password2' : forms.PasswordInput(attrs = {'placeholder': 'Répéter Mot de Passe'}),}


class NewProjectForm(forms.ModelForm):
	class Meta:
		model = Projet
		fields = ('titre','client','prestataire','professionnel','description','prix','date_fin')


