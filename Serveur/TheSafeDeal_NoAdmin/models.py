from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User


# Create your models here.

TYPE_USER = (
	('Prestataire', 'Prestataire'),
	('Professionnel', 'Professionnel'),
	('Client', 'Client')
)

class CustomUser(AbstractUser):
    typeUser = models.CharField(max_length=30, choices=TYPE_USER,null=False, blank=False)
    projet = models.CharField(max_length=32, blank=True)
    
    def add_project(self, clé_projet):
    	if self.projet.find(clé_projet+";") == -1 :
    		self.projet = self.projet + clé_projet +";"

    def delete_projet(self, clé_projet):
    	if self.projet.find(clé_projet+";") != -1 :
    		self.projet = self.projet.replace(clé_projet+";","")

    # RETURN 1 LISTE CONTENANT DES STRINGS CORRESPONDANT AUX KEY DES PROJETS VISIBLES PAR LE USER
    def get_projects_list(self):
    	if self.projet == "" :
    		return []
    	else:
    		result = self.projet.split(';')
    		result.remove("")
    		return result

    # RETURN 2 LISTES CONTENANT DES OBJECTS PROJET : [0] VALIDATED PROJECTS BY THE USER
    #												 [1] NOT VALIDATED PROJECTS BY THE USER
    def get_validated_projects_list(self):
    	user_type = self.typeUser
    	projects_list = self.get_projects_list()
    	validated_projects = []
    	unvalidated_projects = []
    	if len(projects_list) == 0:
    		return [],[]
    	for key_project in projects_list:
    		if user_type == 'Prestataire':
    			if Projet.objects.get(key=key_project).isValidate_Prestataire :
    				validated_projects.append(Projet.objects.get(key=key_project))
    			elif not Projet.objects.get(key=key_project).isValidate_Prestataire :
    				unvalidated_projects.append(Projet.objects.get(key=key_project))
    		elif user_type == 'Professionnel':
    			if Projet.objects.get(key=key_project).isValidate_Professionnel :
    				validated_projects.append(Projet.objects.get(key=key_project))
    			elif not Projet.objects.get(key=key_project).isValidate_Professionnel :
    				unvalidated_projects.append(Projet.objects.get(key=key_project))
    		elif user_type == 'Client':
    			if Projet.objects.get(key=key_project).isValidate_Client :
    				validated_projects.append(Projet.objects.get(key=key_project))
    			elif not Projet.objects.get(key=key_project).isValidate_Client :
    				unvalidated_projects.append(Projet.objects.get(key=key_project))
    	return validated_projects,unvalidated_projects


class Projet(models.Model):
	titre = models.CharField(max_length=200)
	key = models.CharField(max_length=32, unique=True)
	prestataire = models.TextField(max_length=150)
	client = models.TextField(max_length=150, blank=True)
	professionnel = models.TextField(max_length=150)
	date_debut = models.DateTimeField(auto_now_add = True, auto_now=False)
	date_fin = models.DateTimeField(auto_now = False, blank = False)
	description = models.TextField()
	prix = models.DecimalField(max_digits=9, decimal_places=2)
	isValidate_Prestataire = models.BooleanField(default=False)
	isValidate_Professionnel = models.BooleanField(default=False)
	isValidate_Client = models.BooleanField(default=False)

	REQUIERED_FIELDS = []

	def __str__(self):
		return self.titre


