# FONCTIONS UTILITAIRES

from datetime import datetime, timezone
from .models import *
from django.conf import settings
from PIL import Image


# FONCTION QUI RETOURNE UNE LISTE DE DICTIONNAIRES, REPRESENTANT LES PROJETS
def stringify_projects_list(projects_list):
		if len(projects_list) == 0:
			return '{ "projets" = [] }'
		result = '{ "projets" : [ '
		i = 1
		for projet in projects_list :
			result = result + '{ "titre" : "' +  projet.titre + '", "key" : "' + projet.key + '" },'
		result = result[0:-1]
		result = result + '] }'
		return result


# FONCTION QUI RETOURNE L'ETAT DE L'EVENT DE LA DATE ACTUELLE ET DU PROJET (ou None sinon)
def get_actual_state(project_key):
	projet = Projet.objects.get(key = project_key)
	project_events = projet.get_events()
	actual_date = datetime.now(timezone.utc)
	for event in project_events :
		if event.date_debut <= actual_date <= event.date_fin :
			return event.type_event
	return None


# FONCTION QUI RETOURNE L'ETAT DE L'EVENT DE LA DATE RENTREE ET DU PROJET (ou None sinon)
def get_date_state(project_key, date):
	projet = Projet.objects.get(key = project_key)
	project_events = projet.get_events()
	for event in project_events :
		if event.date_debut <= date <= event.date_fin :
			return event.type_event
	return None


# Fonction qui retourne un dictionnaire contenant les noms des utilisateurs correspondant aux emails entrés
def get_usernames_from_emails(email_list):
	result = {}
	for email in email_list :
		try:
			user = CustomUser.objects.get(email = email)
			result[email] = user.username
		except Exception as e:
			pass
	return result


# Fonction qui return une liste de strings contenant tous les emails participant à tous les projets dans la liste entrée
def get_all_emails(projects_list):
	result = []
	for projet in projects_list :
		emails = projet.get_emails()
		for email in emails :
			if not email in result :
				result.append(email)
	return result


# Fonction qui retourne le username du user en fonction de l'email entré (str)
def get_name_from_email(email):
	if CustomUser.objects.filter(email = email).exists() :
		return CustomUser.objects.get(email = email).username
	else :
		return ''

# Fonction qui va enregistrer une image dans le dossier MEDIA dans le dossier du projet (UTILISE POUR LES UPLOAD API)
# Return l'image ouverte avec PIL
def save_image(data,project_key,image_name):
	with open(settings.MEDIA_ROOT+"/"+project_key+"/"+image_name, "wb") as fh:
		fh.write(data)
	#image = Image.open(settings.MEDIA_ROOT+"/"+project_key+"/"+image_name)
	image = open(settings.MEDIA_ROOT+"/"+project_key+"/"+image_name, "r")
	return image

# Fonction qui return le hash à décoder en base 64 à partir d'un encodage (supprime le ';base64,...'')
def get_hash(data):
	i = data.find('base64,')
	i = i + 7
	return data[i:len(data)]

# Fonction qui return l'extension d'une photo uploadée (avant encodage)
def get_extension_pic(data):
	i = data.find(';base64')
	i = i - 1
	j = i
	extension = ''
	while data[i] != '/':
		extension = extension + data[i]
		i = i - 1
	return data[i+1:j+1]
