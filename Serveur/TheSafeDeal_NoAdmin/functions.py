# FONCTIONS UTILITAIRES

from datetime import datetime, timezone
from .models import *

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