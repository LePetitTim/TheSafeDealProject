from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
import os




# Create your models here.

TYPE_USER = (
	('Prestataire', 'Prestataire'),
	('Professionnel', 'Professionnel'),
	('Client', 'Client')
)

class CustomUser(AbstractUser):
    typeUser = models.CharField(max_length=30, choices=TYPE_USER,null=False, blank=False)
    projet = models.CharField(max_length=32, blank=True)
    email = models.EmailField(verbose_name='email address',max_length=255,unique=True,)
    
    def add_project(self, clé_projet):
    	if self.projet.find(clé_projet+";") == -1 :
    		self.projet = self.projet + clé_projet +";"
    		self.save()

    def delete_projet(self, clé_projet):
    	if self.projet.find(clé_projet+";") != -1 :
    		self.projet = self.projet.replace(clé_projet+";","")
    		self.save()

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


    # FUNCTION THAT SETS THE isValidate_[user_type] variable of the project to 1
    def validate_project(self, project_key):
    	user_type = self.typeUser
    	projet = Projet.objects.get(key=project_key)
    	if user_type == 'Prestataire':
    		projet.isValidate_Prestataire = 1
    		projet.save()
    	elif user_type == 'Professionnel':
    		projet.isValidate_Professionnel = 1
    		projet.save()
    	elif user_type == 'Client':
    		projet.isValidate_Client = 1
    		projet.save()

    # FUNCTION THAT REMOVES THE PROJECT FROM THE USER PROJECTS LIST
    def unvalidate_project(self, project_key):
    	user_type = self.typeUser
    	projet = Projet.objects.get(key=project_key)
    	self.delete_projet(project_key)
    	self.save()
    	if user_type == 'Prestataire':
    		projet.prestataire = ''
    		projet.save()
    	elif user_type == 'Professionnel':
    		projet.professionnel = ''
    		projet.save()
    	elif user_type == 'Client':
    		projet.client = ''
    		projet.save()

    # FONCTION QUI RETURN UNE LISTE CONTENANT DES OBJETS FILES DU PROJET ET QUE LE USER PEUT VOIR
    def get_user_and_project_files(self, project_key):
    	media_path = settings.MEDIA_ROOT
    	#filelisting = FileListing(media_path, sorting_order='upload_date')
    	#files = filelisting.walk(project_key)
    	files = os.listdir(media_path+"/"+project_key)
    	documents = Files.objects.all()
    	fichier = []
    	for file in files :
    		if Files.objects.filter(key=file.split(".")[0]).exists():
    			fichier.append(Files.objects.get(key=file.split(".")[0]))

    	result = []
    	if self.typeUser == 'Client' :
    		for file in fichier :
    			if file.typeName == 'contrat' or file.typeName == 'documents_contrat' or file.typeName == 'photos' or file.typeName == 'avancee_pro' :
		            file.original_name = file.remove_extension()
		            result.append(file)
    	elif self.typeUser == 'Prestataire' :
    		for file in fichier :
	        	if file.typeName == 'demande_travaux' or file.typeName == 'photos' or file.typeName == 'avancee_pre' or file.typeName == 'devis' or file.typeName == 'facture':
		            file.original_name = file.remove_extension()
		            result.append(file)
    	elif self.typeUser == 'Professionnel' :
    		for file in fichier :
	        	if file.typeName == 'contrat' or file.typeName == 'documents_contrat' or file.typeName == 'demande_travaux' or file.typeName == 'photos' or file.typeName == 'avancee_pre' or file.typeName == 'devis' or file.typeName == 'facture':
		            file.original_name = file.remove_extension()
		            result.append(file)
    	return result


class Projet(models.Model):
	titre = models.CharField(max_length=200)
	key = models.CharField(max_length=32, unique=True)
	prestataire = models.TextField(max_length=150, blank=True)
	client = models.TextField(max_length=150)
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

def directory_path(instance,filename):
	typeFileName = filename.split(".")[-1]
	return '{0}/{1}'.format(instance.projet_key,instance.key +'.'+typeFileName)

class Files(models.Model):
	typeName = models.CharField(max_length=30,null=True, blank=False)
	projet_key= models.CharField(max_length=32, blank = True)
	document = models.FileField(upload_to=directory_path)
	upload_date = models.DateTimeField(auto_now_add = True, auto_now=False)
	uploaded_by = models.TextField(max_length=150)
	original_name = models.TextField(max_length=150)
	key = models.CharField(max_length=32, unique=True)

	def remove_extension(self):
		return (self.original_name.split(".")[0])
		
class Contract(models.Model):
    projet_key = models.CharField(max_length=32, blank = True, unique= True)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
	

	
