from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Projet
from .models import CustomUser
from .models import Files

PRO_CHOICES = (('Contrat', 'Contrat'),
	('Devis', 'Devis'),
	('Facture', 'Facture'))

PRESTATAIRE_CHOICES = (('Avance', 'Avance'),
	('Devis', 'Devis'),
	('Facture', 'Facture'))

CLIENT_CHOICE = (('Document pour Contrat', 'Document pour Contrat'))

class FileForm(forms.ModelForm):
	class Meta:
		model = Files
		fields = ('typeName','document', )
	def __init__(self, *args, **kwargs):
		typeUser = user.typeuser
		super(FileForm, self).__init__(*args, **kwargs)
		if typeUser == "prestataire":
			self.fields['typeName'].choices = PRESTATAIRE_CHOICES
		else:
			self.fields['typeName'].choices = CLIENT_CHOICE


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

class NewProjectForm(forms.ModelForm):
	class Meta:
		model = Projet
		fields = ('titre','client','prestataire','professionnel','description','prix','date_fin')



    

