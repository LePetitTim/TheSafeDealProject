# FONCTIONS UTILITAIRES

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