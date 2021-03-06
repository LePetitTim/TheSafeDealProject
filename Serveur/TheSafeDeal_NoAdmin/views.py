from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import SignupForm
from .forms import NewProjectForm
from .forms import FileForm
from .forms import ContractForm
from .forms import EventForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.utils.crypto import get_random_string
from django.utils import timezone
from django import forms
from django.contrib.auth import get_user_model, authenticate
from .models import CustomUser, Projet, Files, Contract
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import os
from django.views.decorators.csrf import csrf_exempt
import json
from .functions import *
import time
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
import base64
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
# Definition des vues Django. Permet de recuperer les informations dans la base de donnée, faire les redirections sur les autres pages.
# L'affichage de la page actuel ...



def home(request):
	"""
	Affiche la page d'accueil
	"""
	file = Files.objects.all()
	customUser = CustomUser.objects.all()
	return render(request, 'home.html', {'CustomUser' : customUser, 'CustomFile' : file})

def register(request):
	"""
	Affiche la page registration.
	SI le formulaire est valide, le compte est crée mais inactif. L'utilisateur doit se connecter à sa boite mail pour activer son compte.
	(/!\ Serveur SMTP bloqué, besoin de modifier les parametres dans : TheSafeDeal/settings.py pour envoyer sur un serveur SMTP fonctionnel).
	Envoie un mail avec comme objet : Active ton compte provenant de l'adresse mail du serveur SMTP. Avec comme description la page acc_active_email.html.
	La page contient un token unique pour l'activation du compte. L'url pour l'activation utilise ce token.
	"""
	if request.method == 'POST':
		form = SignupForm(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			#Remove user.is_active = True + put other part + change SMTP in settings
			user.is_active = True
			user.save()
			return redirect('home')
			"""
			user.is_active = False
			user.save()
			current_site = get_current_site(request)
			mail_subject = 'Active ton compte.'
			message = render_to_string('acc_active_email.html', {
				'user': user,
				'domain': current_site.domain,
				'uid':urlsafe_base64_encode(force_bytes(user.pk)),
				'token':account_activation_token.make_token(user),
			})
			to_email = form.cleaned_data.get('email')
			email = EmailMessage(
						mail_subject, message, to=[to_email]
			)
			email.send()
			return HttpResponse("Veuillez s'il vous plait confirmer votre email pour completer le processus")
			"""
	else:
		form = SignupForm()
	return render(request, 'register.html', {'form': form, 'titre' : "S'enregistrer"})

def activate(request, uidb64, token):
	"""
	Utilisé pour l'activation du compte. Si le token n'existe pas(url crée de toute pièce). Affichage d'un message d'erreur.
	"""
	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		User = get_user_model()
		user = User.objects.get(pk=uid)
	except(TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None
	if user is not None and account_activation_token.check_token(user, token):
		user.is_active = True
		user.save()
		login(request, user)
		return redirect('home')
	else:
		return HttpResponse("Le lien d'activation est invalide!")
		
def showProject(request, uidb32):
	"""
	Affiche le projet avec la clé uidb32. La clé est unique.
	Le projet est affiché sous certaines conditions : 
	- l'utilisateur doit etre authentifié.
	- le projet doit exister
	- L'utilisateur doit faire partie du projet.
	
	Cette page affiche en détail les fichiers du projet. Les differents éléments utiles provenant du modèle Projet.
	Possibilité d'ajouter un prestataire si il n'est pas choisie a la création.
	Possibilité de télécharger les fichiers du projet.
	Possibilité d'atteindre le contrat de se projet. (voir contract).
	"""
	valide = ""
	client=""
	professionnel=""
	prestataire=""
	if request.user.is_authenticated():
		utilisateur = CustomUser.objects.get(username=request.user)
		if Projet.objects.filter(key=uidb32).exists(): 
			project = Projet.objects.get(key=uidb32)
		else:
			valide = "Le Projet n'existe pas."
			return render(request, 'project.html',{'valide':valide, 'titre' : 'Deal with it'})

		user = CustomUser.objects.all()
		for i in user:
			if project.prestataire == i.email:
				prestataire = i.username
			if project.client == i.email:
				client = i.username
			if project.professionnel == i.email:
				professionnel = i.username
		if request.user.username != prestataire and request.user.username != client and request.user.username != professionnel :
			valide = "Vous n'avez pas accès à ce projet."
			return render(request, 'project.html',{'valide':valide})

		documents_list_of_user_of_project = utilisateur.get_user_and_project_files(uidb32)
		if request.method == "POST":
			if 'email' in request.POST :
				email_new_prestataire = request.POST['email']
				if CustomUser.objects.filter(email=email_new_prestataire).exists() :
					new_prestataire = CustomUser.objects.get(email=email_new_prestataire)
					if new_prestataire.typeUser == 'Prestataire':
						project.prestataire = email_new_prestataire
						project.save()
						new_prestataire.add_project(uidb32)
						prestataire = new_prestataire.username
						valide = "Prestataire ajouté avec succès!"
						return render(request, 'project.html',{'projet':project, 'valide':valide, 'nameClient' : client, 'nameProfessionnel': professionnel, 'namePrestataire': prestataire, 'project_key': project.key, 'files' :documents_list_of_user_of_project})
						#return redirect(uidb32)
					else:
						valide = "L'utilisateur entré n'est pas un Prestataire."
						return render(request, 'project.html',{'projet':project, 'valide':valide, 'nameClient' : client, 'nameProfessionnel': professionnel, 'namePrestataire': prestataire, 'project_key': project.key, 'files' : documents_list_of_user_of_project})
			elif request.FILES :
				form = FileForm(request.POST,request.FILES)
				if form.is_valid():
					new_document = form.save(commit=False)
					new_document.projet_key = uidb32
					new_document.typeName = request.POST['typeName']
					new_document.uploaded_by = CustomUser.objects.get(username=request.user).username
					original_name = str(request.FILES['document'])
					new_document.original_name = original_name
					new_document.extension = new_document.get_extension()
					new_document.key = get_random_string(length=32)
					new_document.save()
					documents_list_of_user_of_project = utilisateur.get_user_and_project_files(uidb32)
					valide = "Votre document a bien été uploadé !"
			else:
				valide = "Aucun utilisateur trouvé à cette adresse email."
				return render(request, 'project.html',{'projet':project, 'valide':valide, 'nameClient' : client, 'nameProfessionnel': professionnel, 'namePrestataire': prestataire, 'project_key': project.key, 'files' : documents_list_of_user_of_project})

		if request.method == "GET":
			if 'delete' in request.GET :
				if Files.objects.filter(key=request.GET['delete']):
					delete_file = Files.objects.get(key=request.GET['delete'])
					if utilisateur.username == delete_file.uploaded_by :
						delete_file.delete()
						os.remove(settings.MEDIA_ROOT+"/"+str(delete_file.document))
						documents_list_of_user_of_project = utilisateur.get_user_and_project_files(uidb32)
						return redirect("/project/"+project.key)
		return render(request, 'project.html',{'projet':project, 'valide':valide, 'nameClient' : client, 'nameProfessionnel': professionnel, 'namePrestataire': prestataire, 'project_key': project.key, 'files' : sorted(documents_list_of_user_of_project, key=lambda files: files.upload_date, reverse=True), 'state' : get_actual_state(project.key)})
	else:
		valide = "Veuillez vous connecter pour voir cette page."
		return render(request, 'project.html',{'valide':valide})

def connected(request):
	"""
	Affiche tous les projets de l'utilisateur, permet d'ajouter, d'activer ou refuser un projet.
	
	Cette page s'affiche normalement sous certaines conditions : 
	- l'utilisateur doit etre authentifié.

	Cette page affiche en détail chaque projet de l'utilisateur. Permet également de rajouter un nouveau projet.
	Si le formulaire pour l'ajout d'un nouveau projet est valide, le projet est inactif et il suffit d'appuyer sur le bouton valider 
	(et que chaque utilisateur le fasse) pour que le projet soit accepté et visible pour chacun.
	"""
	user = request.user
	if user.is_authenticated() :
		utilisateur = CustomUser.objects.get(username=request.user)
		validated_projects = utilisateur.get_validated_projects_list()[0]
		unvalidated_projects = utilisateur.get_validated_projects_list()[1]

		if request.method == "POST":
			form = NewProjectForm(request.POST)

			if form.is_valid(): 
				cleaned_info = form.cleaned_data
				new_project = form.save(commit=False)
				new_project.key = get_random_string(length=32)
				new_project.date_debut = timezone.now()

				if utilisateur.email != cleaned_info['client'] and utilisateur.email != cleaned_info['professionnel'] and utilisateur.email != cleaned_info['prestataire'] :
					error = "Vous ne pouvez pas créer un projet sans en faire partie! Voyons..."
					return render(request, 'connected.html',{'form':form, 'error': error, 'validated_projects':validated_projects, 'unvalidated_projects':unvalidated_projects}) 

				if CustomUser.objects.filter(email = cleaned_info['client']).exists() and CustomUser.objects.filter(email = cleaned_info['professionnel']).exists():
					if cleaned_info['prestataire'] == '':
						cli = CustomUser.objects.get(email = cleaned_info['client'])
						pro = CustomUser.objects.get(email = cleaned_info['professionnel'])
						if cli.typeUser == 'Client' and pro.typeUser == 'Professionnel':
							new_project.save()
							cli.add_project(new_project.key)
							pro.add_project(new_project.key)
							os.mkdir(settings.MEDIA_ROOT+"/"+new_project.key)
							return redirect(connected)
						else:
							error = "Oups! L'adresse email entrée du Professionnel ou Client ne correpond pas à la bonne personne!"
							return render(request, 'connected.html',{'form':form, 'error': error, 'validated_projects':validated_projects, 'unvalidated_projects':unvalidated_projects})
					else:
						if CustomUser.objects.filter(email = cleaned_info['prestataire']).exists():
							pre = CustomUser.objects.get(email = cleaned_info['prestataire'])
							pro = CustomUser.objects.get(email = cleaned_info['professionnel'])
							cli = CustomUser.objects.get(email = cleaned_info['client'])
							if pre.typeUser == 'Prestataire' and pro.typeUser == 'Professionnel' and cli.typeUser == 'Client':
								new_project.save()
								pre.add_project(new_project.key)
								pro.add_project(new_project.key)
								cli.add_project(new_project.key)
								os.mkdir(settings.MEDIA_ROOT+"/"+new_project.key)
								return redirect(connected)
							else:
								error = "Oups! L'adresse email entrée du Professionnel ou Prestataire ou Client ne correpond pas à la bonne entité !"
								return render(request, 'connected.html',{'form':form, 'error': error, 'validated_projects':validated_projects, 'unvalidated_projects':unvalidated_projects})
						else:
							error = "Le Prestataire n'est pas enregistré à cette adresse mail, veuillez réessayer."
							return render(request, 'connected.html',{'form':form, 'error': error, 'validated_projects':validated_projects, 'unvalidated_projects':unvalidated_projects})
				else:
					if not CustomUser.objects.filter(email = cleaned_info['client']).exists():
						error = "Le Client n'est pas enregistré à cette adresse mail, veuillez recréer le projet."
					elif not CustomUser.objects.filter(email = cleaned_info['professionnel']).exists():
						error = "Le Professionnel n'est pas enregistré à cette adresse mail, veuillez recréer le projet."
					return render(request, 'connected.html',{'form':form, 'error': error, 'validated_projects':validated_projects, 'unvalidated_projects':unvalidated_projects})
		
		elif request.method == 'GET' and 'key' in request.GET and 'validate' in request.GET :
			key = request.GET['key']
			validate = request.GET['validate']
			if validate == 'True' :
				utilisateur.validate_project(key)
			elif validate == 'False':
				utilisateur.unvalidate_project(key)
			return redirect(connected)
		else:
			form = NewProjectForm()
		return render(request, 'connected.html',{'form':form, 'user':request.user, 'validated_projects':validated_projects, 'unvalidated_projects':unvalidated_projects})
	else:
		form = NewProjectForm()

	return render(request, 'connected.html',{'form':form, 'user':request.user})

def download(request, project_key, document_key):
	"""
	Permet de télécharger les fichiers du projet. Chaque projet a son propre dossier avec tous les elements.
	Cette vue utilise le modele File pour envoyer les fichiers.

	Cette fonctionnalité est possible normalement uniquement lorsque : 
	- l'utilisateur doit etre authentifié.

	"""
	if request.user.is_authenticated():
		utilisateur = CustomUser.objects.get(username=request.user)
		if request.method == 'POST':
			if request.POST['download']:
				if Files.objects.filter(key=document_key).exists() :
					document = Files.objects.get(key=document_key)
				else:
					redirect(showProject)
				if Projet.objects.filter(key=project_key).exists():
					projet = Projet.objects.get(key=project_key)
				else:
					redirect(showProject)
				if document in utilisateur.get_user_and_project_files(project_key):
					with open(settings.MEDIA_ROOT+"/"+str(document.document), 'rb') as fh:
						response = HttpResponse(fh.read(), content_type="application/force-download")
						response['Content-Disposition'] = 'inline; filename=' + document.original_name
						return response
				else:
					valide = "Vous n'avez pas les droits d'accès à ce fichier."
					return render(request, 'project.html',{'valide':valide})

		return redirect("/project/"+project_key)
	else:
		valide = 'Veuillez vous connecter pour accéder à cette fonctionnalité.'
		return render(request, 'project.html',{'valide':valide})

def contract(request, uidb32):
	"""
	Permet d'afficher le contrat d'un projet, permet de le modifier en tant que professionnelle et l'afficher en tant que Client.

	Il est egalement possible de le modifier pour le Professionnelle et le telecharger pour le client et le professionnelle.
	
	La page s'affiche est possible normalement uniquement lorsque : 
	- l'utilisateur est authentifié.
	- l'utilisateur n'est pas un prestataire
	- le contrat existe (sauf pour professionnelle -> Formulaire pour la creation d'un nouveau contrat)
	- le projet existe

	"""
	telecharger = False
	save = False
	contractExist=False
	if request.user.is_authenticated():
		project = Projet.objects.get(key=uidb32)
		user = CustomUser.objects.all()
		for i in user:
			if project.prestataire == i.email:
				prestataire = i.username
			if project.client == i.email:
				client = i.username
			if project.professionnel == i.email:
				professionnel = i.username
		if request.user.username != prestataire and request.user.username != client and request.user.username != professionnel :
			valide = "Vous n'avez pas accès à ce projet."
			return render(request, 'project.html',{'valide':valide})
		if request.user.typeUser == 'Prestataire':
			valide = "Vous n'avez pas accès aux contrats."
			return render(request, 'project.html',{'valide':valide})
		elif request.user.typeUser == 'Professionnel':
			if request.method == "POST" and 'new' in request.POST:
				form = ContractForm(request.POST)
				if form.is_valid():
					new_contract = form.save(commit=False)
					new_contract.projet_key = uidb32
					new_contract.created_date = timezone.now()
					new_contract.save()
					save = True
					return render(request, 'contract.html', {'contract':new_contract, 'save':save})
			elif request.method == "POST" and "edit" in request.POST:
				post = get_object_or_404(Contract, projet_key=uidb32)
				form = ContractForm(request.POST, instance=post)
				if form.is_valid():
					new_contract = form.save(commit=False)
					new_contract.projet_key = uidb32
					new_contract.created_date = timezone.now()
					new_contract.save()
					save = True
					telecharger = True
					return render(request, 'contract.html', {'contract':new_contract, 'save':save, 'telecharger':telecharger})	 
				form = ContractForm(instance=post)
				return render(request, 'contract.html', {'contract':form,'save':save})
			elif request.method == "POST" and "delete" in request.POST:
				try:
					instance = Contract.objects.get(projet_key=uidb32)
					instance.delete()
					
				except ObjectDoesNotExist:
					pass
				valide = "Le contrat a été supprimé"
				return render(request, 'project.html', {'valide':valide})
			elif request.method == "POST" and "download" in request.POST:
				new_contract = Contract.objects.get(projet_key=project.key)
				fichier = open(settings.MEDIA_ROOT +"/"+project.key+"/"+"contrat.txt", "w")
				fichier.write("Créé le "+str(new_contract.created_date)+"\n"+new_contract.title+"\n \n"+new_contract.text)
				fichier.close()

				with open(settings.MEDIA_ROOT +"/"+project.key+"/"+"contrat.txt", 'rb') as fh:
						response = HttpResponse(fh.read(), content_type="application/force-download")
						response['Content-Disposition'] = 'inline; filename=contrat.txt'
						return response
			else:
				user = CustomUser.objects.all()					
				if Projet.objects.filter(key=uidb32).exists():
					if Contract.objects.filter(projet_key=uidb32).exists():
						save = True
						contract =  Contract.objects.get(projet_key=uidb32)
						contractExist = 'True'
						telecharger = True
						return render(request, 'contract.html', {'contract':contract,'save':save,'telecharger':telecharger})
					else:
						form = ContractForm()
						contract=""
						error = "Il n'y a pas encore de contrat pour ce projet."
						return render(request, 'contract.html',{'contract':contract ,'error':error, 'form':form})
				else:
					valide = "Le Projet n'existe pas."
					return render(request, 'project.html',{'valide':valide})
		elif request.user.typeUser == 'Client':
			if request.method == "POST" and 'download' in request.POST:
				new_contract = Contract.objects.get(projet_key=project.key)
				fichier = open(settings.MEDIA_ROOT +"/"+project.key+"/"+"contrat.txt", "w")
				fichier.write("Créé le "+str(new_contract.created_date)+"\n"+new_contract.title+"\n \n"+new_contract.text)
				fichier.close()

				with open(settings.MEDIA_ROOT +"/"+project.key+"/"+"contrat.txt", 'rb') as fh:
						response = HttpResponse(fh.read(), content_type="application/force-download")
						response['Content-Disposition'] = 'inline; filename=contrat.txt'
						return response

			if Projet.objects.filter(key=uidb32).exists():
				if Contract.objects.filter(projet_key=uidb32).exists():
					contract =  Contract.objects.get(projet_key=uidb32)
					contractExist = 'True'
					telecharger = True
					return render(request, 'contract.html', {'contract':contract,'Exist':contractExist,'telecharger':telecharger})
				else:
					contract=""
					error = "Il n'y a pas encore de contrat pour ce projet."
					return render(request, 'contract.html',{'contract':contract ,'error':error})
			else:
				valide = "Le Projet n'existe pas."
				return render(request, 'project.html',{'valide':valide})

	else:
		valide = "Veuillez vous connecter pour voir cette page."
		return render(request, 'project.html',{'valide':valide})


@csrf_exempt
def api_token(request):
	if not request.user.is_authenticated():
		if request.method == 'POST':
			body = request.body
			body_decoded = body.decode('utf8')
			data_json = json.loads(body_decoded)
			username = data_json['username']
			password = data_json['password']
			token = get_random_string(length=60)
			authentification = authenticate(username=username, password=password)
			if authentification is not None :
				utilisateur = CustomUser.objects.get(username=username)
				utilisateur.api_token = token
				utilisateur.save()
				login(request, utilisateur)
				session = request.session
				response = HttpResponse(content='{ "token" : '+ '"'+token+'"' +'}')
				response.set_cookie(key='sessionid', value=session)
				return response
			else :
				return HttpResponse("NO_ACCOUNT")
		else :
			return HttpResponse("NO_POST")
	logout(request)
	return HttpResponse("Vous êtes déjà connecté, veuillez vous re-login")


def api_projects(request, token):
	users = CustomUser.objects.all()
	if CustomUser.objects.filter(api_token = token).exists():
		utilisateur = CustomUser.objects.get(api_token = token)
		projects = utilisateur.get_validated_projects_list()[0]
		return HttpResponse(stringify_projects_list(projects))
	else:
		return HttpResponse('Aucun compte trouvé pour ce token')

@csrf_exempt
def api_upload(request, token, project_key):
	if request.method == 'POST' :
		body = request.body
		body_decoded = body.decode('utf8')
		data_json = json.loads(body_decoded)
		list_picts = data_json['files']
		error = []
		for data in list_picts:
			new_original_name = "upload_"+str(get_random_string(5))+"."+get_extension_pic(data)
			new_key = get_random_string(length=32)
			image_name_bdd = new_key+"."+get_extension_pic(data)
			try:
				hashe = get_hash(data)
				decoded = base64.b64decode(hashe)
				new_doc = InMemoryUploadedFile(ContentFile(decoded), None, new_original_name, 'image/'+get_extension_pic(data), ContentFile(decoded).tell, None)
			except Exception as e:
				error.append("La "+str(list_picts.index(data)+1)+"è image importée est corrompue ou mal encodée. ")
				continue
			new_projet_key = project_key
			new_typeName = "photos"
			try:
				new_uploaded_by = CustomUser.objects.get(api_token=token).username
			except Exception as e:
				return HttpResponse("Le token a expiré, veuillez recommencer")
			new_document = Files.objects.create(document=new_doc,typeName=new_typeName,projet_key=project_key,uploaded_by=new_uploaded_by,original_name=new_original_name,key=new_key)
			new_document.extension = new_document.get_extension()
			new_document.save()
		if len(error) != 0 :
			http_response = ""
			for erreur in error :
				http_response = http_response + erreur
			http_response = http_response + "Veuillez recommencer."
			return HttpResponse(http_response)
		return HttpResponse('Les photos ont bien été uploadées.')
	else :
		return HttpResponse('NO_POST')


def about(request):
	"""
	Affiche la page a propos.
	"""
	return render(request, 'about.html',{})
def getAllYear(year,uidb32,date_projet):
	r={}
	for i in range(0,len(year)):
		m=0
		yea={}
		d=0
		date = time.mktime(datetime.strptime(str(year[i]) + '-01-01', "%Y-%m-%d").timetuple())
		last_of_the_year = time.mktime(datetime.strptime(str(year[i]) + '-12-31', "%Y-%m-%d").timetuple())
		while date <= last_of_the_year:
			y = datetime.fromtimestamp(date).year
			if m !=datetime.fromtimestamp(date).month:
				month={}
			m = datetime.fromtimestamp(date).month
			if d !=datetime.fromtimestamp(date).day:
				couleur={}
			d = datetime.fromtimestamp(date).day
			w = datetime.fromtimestamp(date).weekday()
			c = define_color_event(date,uidb32)
			couleur[w] = c
			month[d] = couleur
			yea[m]=month
			r[y]=yea
			date =date+24*3600
	return r

def define_color_event(date,projet_key):
	datesProjet = Event.objects.all().filter(projet_key=projet_key)
	couleur="B"
	for i in datesProjet:
		date_debut_Projecti = i.date_debut.timestamp()
		date_fin_Projecti = i.date_fin.timestamp()
		if date_debut_Projecti <= date and date_fin_Projecti >= date:            
			if i.type_event == "En Travaux":
				couleur = "R"
			elif i.type_event == "Loué":
				couleur = "V"
			elif i.type_event == "En cours de reservation":
				couleur = "O"
			else:
				couleur = "B"
			return couleur
	return couleur

def event(request,uidb32):
    if request.user.is_authenticated():     
        if request.method == "POST":
            form = EventForm(request.POST)
            if form.is_valid():
                event = form.save(commit=False)
                if event.check_date_event(uidb32,event.date_debut,event.date_fin):
                    if request.user.typeUser=='Client':
                        event.projet_key=uidb32
                        event.type_event='En cours de reservation'
                        event.save()
                        form= EventForm()
                        information = "L'evenement a bien été rajouté, il faut attendre la validation du professionnel"
                        render(request, 'about.html',{'form': form,'information':information, 'uidb32' : uidb32})
                    else:
                        event.projet_key=uidb32
                        event.type_event='En Travaux'
                        event.save()
                        form= EventForm()
                        information = "L'evenement a bien été rajouté"
                        render(request, 'about.html',{'form': form,'information':information, 'uidb32' : uidb32})
                else:
                    form = EventForm()
                    information = "Les dates sont dejà prises"
                    render(request, 'about.html',{'form': form,'information': information, 'uidb32' : uidb32})
        else:
            form = EventForm()
            information = ""
        date_projet = Event.objects.all().filter(projet_key=uidb32)
        year = []
        if date_projet.count()!=0:
            debut_year = date_projet[0].date_debut.year
            fin_year = date_projet[0].date_fin.year
            for i in range(0,len(date_projet)):
                if debut_year not in year:
                    year.append(debut_year)
                debut_year = date_projet[i].date_debut.year
                if fin_year not in year:
                    year.append(fin_year)
                fin_year = date_projet[i].date_fin.year
            tabYear = getAllYear(year,uidb32,date_projet)
            if request.user.typeUser=='Professionnel':
                date_projet_a_reserver=date_projet.filter(type_event="En cours de reservation")
                return render(request, 'event.html',{'form': form,'information': information,'dates':date_projet,'tabYear':tabYear,'reserver':date_projet_a_reserver, 'uidb32' : uidb32})
            elif request.user.typeUser=='Client':
                date_projet_loue=date_projet.filter(type_event="Loué")
                date_projet_a_reserver=date_projet.filter(type_event="En cours de reservation")
                return render(request, 'event.html',{'form': form,'information': information,'dates':date_projet,'tabYear':tabYear,'loue':date_projet_loue,'reserver':date_projet_a_reserver, 'uidb32' : uidb32})
            else:
                return render(request, 'event.html',{'form': form,'information': information,'dates':date_projet,'tabYear':tabYear, 'uidb32' : uidb32})
        else:
            #Changer 2018 par la valeur dynamique de l'année actuelle, si besoin.
            tabYear=getAllYear([2018],uidb32,date_projet)            
            return render(request, 'event.html',{'form': form,'information': information,'tabYear':tabYear, 'uidb32' : uidb32})        
    else:
        return redirect('home')

def add_event(request,uidb32,id):
    date_projet=Event.objects.all().filter(projet_key=uidb32).filter(id=id)
    date_projet.update(type_event='Loué')
    return redirect('event',uidb32=uidb32)

def delete_event(request,uidb32,id):
    date_projet=Event.objects.all().filter(projet_key=uidb32).filter(id=id)
    date_projet.delete()
    return redirect('event',uidb32=uidb32)

