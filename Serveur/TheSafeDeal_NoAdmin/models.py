from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
import os




# Create your models here.

# Django va transformer ce fichier python en un fichier sql pour la base de donnée db.sqlite3

TYPE_USER = (
	('Prestataire', 'Prestataire'),
	('Professionnel', 'Professionnel'),
	('Client', 'Client')
)
TYPE_EVENT = (
    ('Disponible', 'Disponible'),
    ('En Travaux', 'En Travaux'),
    ('Loué', 'Loué'),
    ('En cours de reservation', 'En cours de reservation'),
)

class CustomUser(AbstractUser):
    '''
    Modèle pour les utilisateurs. Il contient toutes les infos d'un utilisateur ainsi que les projets de l'utilisateur cléprojet1;cléprojet2;cléprojet3.
    
    Le modèle est fait des tables de base du modèle Django AbstractUser avec :
    password (le mot de passe est encrypyé dans la base de donnée utilisant sha)
    last_login
    is_superuser
    username
    first_name (non utilisé)
    last_name (non utilisé)
    is_staff
    is_active
    date_joined
    type_user
    projet
    email
    '''
    typeUser = models.CharField(max_length=30, choices=TYPE_USER,null=False, blank=False)
    projet = models.CharField(max_length=32, blank=True)
    email = models.EmailField(verbose_name='email address',max_length=255,unique=True,)
    api_token = models.CharField(max_length=100, blank=True)
    
    def add_project(self, clé_projet):
    	if self.projet.find(clé_projet+";") == -1 :
    		self.projet = self.projet + clé_projet +";"
    		self.save()

    def delete_projet(self, clé_projet):
    	if self.projet.find(clé_projet+";") != -1 :
    		self.projet = self.projet.replace(clé_projet+";","")
    		self.save()


    # RETURN 1 LISTE CONTENANT DES OBJETS PROJET CORRESPONDANT PROJETS VISIBLES PAR LE USER
    def get_projects_list(self):
    	if self.projet == "" :
    		return []
    	else:
    		projets = Projet.objects.all()
    		result = []
    		if self.typeUser == 'Professionnel' :
    			for projet in projets :
    				if projet.professionnel == self.email:
    					result.append(projet)
    		elif self.typeUser == 'Client' :
    			for projet in projets :
    				if projet.client == self.email:
    					result.append(projet)
    		elif self.typeUser == 'Prestataire' :
    			for projet in projets :
    				if projet.prestataire == self.email:
    					result.append(projet)
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
    	for projet in projects_list:
    		if user_type == 'Prestataire':
    			if Projet.objects.get(key=projet.key).isValidate_Prestataire :
    				validated_projects.append(Projet.objects.get(key=projet.key))
    			elif not Projet.objects.get(key=projet.key).isValidate_Prestataire :
    				unvalidated_projects.append(Projet.objects.get(key=projet.key))
    		elif user_type == 'Professionnel':
    			if Projet.objects.get(key=projet.key).isValidate_Professionnel :
    				validated_projects.append(Projet.objects.get(key=projet.key))
    			elif not Projet.objects.get(key=projet.key).isValidate_Professionnel :
    				unvalidated_projects.append(Projet.objects.get(key=projet.key))
    		elif user_type == 'Client':
    			if Projet.objects.get(key=projet.key).isValidate_Client :
    				validated_projects.append(Projet.objects.get(key=projet.key))
    			elif not Projet.objects.get(key=projet.key).isValidate_Client :
    				unvalidated_projects.append(Projet.objects.get(key=projet.key))
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
	        	if file.typeName == 'contrat' or file.typeName == 'documents_contrat' or file.typeName == 'demande_travaux' or file.typeName == 'photos' or file.typeName == 'avancee_pre' or file.typeName == 'devis' or file.typeName == 'facture' or file.typeName == 'avancee_pro' :
		            file.original_name = file.remove_extension()
		            result.append(file)
    	return result


class Projet(models.Model):
	"""
    Modèle pour les projets. Il contient les informations de 1 projet.
    
    Le modèle est fait des tables :
    titre
    clé du projet
    email du prestataire
    email du client
    email du professionnel
    date de debut du projet
    date de fin du projet
    description
    prix
    3 booleans pour la validations de chaque personnes
    """
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
	"""
    Modèle pour les fichiers. Il contient les informations de 1 Fichier.
    Chaque fichier se situe dans son dossier correspondant au projet.

    Le modèle est fait des tables :
    type du fichier
    clé du projet (l'endroit ou il se situera dans le dossier des fichiers : /media)
    url du fichier
    date d'upload
    nom de celui qui a upload le fichier
    nom original (sur le pc de l'utilisateur)
    clé du fichier
    extension du fichier (.txt ,.pdf ...)
    """
	typeName = models.CharField(max_length=30,null=True, blank=False)
	projet_key= models.CharField(max_length=32, blank = True)
	document = models.FileField(upload_to=directory_path)
	upload_date = models.DateTimeField(auto_now_add = True, auto_now=False)
	uploaded_by = models.TextField(max_length=150)
	original_name = models.TextField(max_length=150)
	key = models.CharField(max_length=32, unique=True)
	extension = models.CharField(max_length=20, blank=True)

	def remove_extension(self):
		return (self.original_name.split(".")[0])

	def get_extension(self):
		try:
			return str(self.document).split(".")[-1]
		except Exception as e:
			return ""

	def extension_has_uppercase(self):
		for char in self.extension :
			if ord(char) >= 65 and ord(char) <= 90 :
				return True
		return False

	def put_extension_lowercase_everywhere(self):
		extension = self.extension
		for char in extension :
			if ord(char) >= 65 and ord(char) <= 90 :
				char = char.replace(char,char(ord(char+27)))
		return extension


class Contract(models.Model):
    """
    Modèle pour les contrats. Il contient les informations de chaque contrats.
    
    Le modèle est fait des tables :
    clé du projet.
    titre du contrat
    description du contrat
    date de creation du contrat.
    """
    projet_key = models.CharField(max_length=32, blank = True, unique= True)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
	


class Event(models.Model):
    projet_key = models.CharField(max_length=32, blank = True, unique= False)
    date_debut = models.DateTimeField(auto_now = False, blank = False)
    date_fin = models.DateTimeField(auto_now = False, blank = False)
    type_event = models.CharField(max_length=30, choices=TYPE_EVENT, null=False, blank=False)

# Verifie si la date ne fait pas partie d'un autre evenement.
    def check_date_event(self):
        debut = self.date_debut.now()
        fin = self.date_fin.now()
        datesProject = Event.objects.get(projet_key=self.projet_key)
        for i in datesProject:
            date_debut_Projecti = i.date_debut
            date_fin_Projecti = i.date_fin
            if date_debut_Projecti<fin and date_debut_Projecti>debut:
                return False
            if date_fin_Projecti.total_seconds<fin and date_fin_Projecti>debut:
                return False
        return True


# Verifie si le type d'evenement n'ai pas innapropprié à la date (ex : construction hors des dates du projet.) ???
    def check_type_event(self,date_debut,date_fin,typeEvent,project_key):
        debutProjet = Project.objects.get(key=project_key).date_debut.total_seconds()
        finProjet = Project.objects.get(key=project_key).date_fin.total_seconds()
        return True


    def __unicode__(self):
        return u'%s' % self.projet_key
