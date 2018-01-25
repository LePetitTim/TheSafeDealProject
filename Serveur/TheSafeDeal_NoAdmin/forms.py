from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Projet
from .models import CustomUser
from .models import Files
from .models import Contract
from .models import Event

# Differents choix de fichier. Chaque type de user peut choisir uniquement ses types de fichier.

PRO_CHOICES = (('Contrat', 'Contrat'),
	('Devis', 'Devis'),
	('Facture', 'Facture'))

PRESTATAIRE_CHOICES = (('Avance', 'Avance'),
	('Devis', 'Devis'),
	('Facture', 'Facture'))

CLIENT_CHOICE = (('Document pour Contrat', 'Document pour Contrat'))

# Formulaire pour les Fichiers utilisant le modele Files (voir models.Files) utilisant les types possibles (voir ci-dessus) et l'url du fichier.
class FileForm(forms.ModelForm):
	class Meta:
		model = Files
		fields = ('typeName','document', )


# Formulaire pour la registration. Utilisant le modele CustomUser (voir models.CustomUser). 
# Le formulaire a les meme champs que UserCreationForm provenant de Django.
class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=100, help_text='Required', widget=forms.TextInput(attrs={'placeholder': 'Entrer Email'}))
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2','typeUser')
        labels = {
        	"typeUser": "Vous êtes un :"
        }
		# Permet de definir le placeholder dans le formulaire.
        widgets = {
        	'password1' : forms.PasswordInput(attrs = {'placeholder': 'Entrer Mot de Passe'}),
            'username' : forms.TextInput(attrs = {'placeholder': 'Entrer Username'}),
            'password2' : forms.PasswordInput(attrs = {'placeholder': 'Répéter Mot de Passe'}),}

# Formulaire pour la création d'un nouveau projet. Utilisant le modele Projet (voir models.Projet)		
class NewProjectForm(forms.ModelForm):
	class Meta:
		model = Projet
		fields = ('titre','client','prestataire','professionnel','description','prix','date_fin')

# Formulaire pour la création d'un nouveau contrat. Utilisant le modele Projet (voir models.Projet)	
class ContractForm(forms.ModelForm):
	class Meta:
		model = Contract 
		fields = ('title', 'text',)

class EventForm(forms.ModelForm):
	class Meta:
		model = Event
		fields = ('date_debut','date_fin','type_event')
		widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date','min':"2018-01-01",'max':"2100-01-01" }),
            'date_fin': forms.DateInput(attrs={'type': 'date','min':"2018-01-01",'max':"2100-01-01"})
        }
    

