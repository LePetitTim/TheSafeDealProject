from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .forms import SignupForm
from .forms import NewProjectForm
from .forms import FileForm
from .forms import ContractForm
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
from django.contrib.auth import get_user_model
from .models import CustomUser, Projet, Files, Contract
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import os

# Create your views here.

def about(request):
    return render(request, 'about.html',{})

def home(request):
	file = Files.objects.all()
	customUser = CustomUser.objects.all()
	return render(request, 'home.html', {'CustomUser' : customUser, 'CustomFile' : file})

def register(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
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
    else:
        form = SignupForm()
    return render(request, 'register.html', {'form': form})

def activate(request, uidb64, token):
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
            return render(request, 'project.html',{'valide':valide})

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
                    new_document.uploaded_by = CustomUser.objects.get(username=request.user).username + " ("+ CustomUser.objects.get(username=request.user).typeUser +")"
                    new_document.original_name = request.FILES['document']
                    new_document.key = get_random_string(length=32)
                    new_document.save()
                    documents_list_of_user_of_project = utilisateur.get_user_and_project_files(uidb32)
                    valide = "Votre document a bien été uploadé !"
            else:
                valide = "Aucun utilisateur trouvé à cette adresse email."
                return render(request, 'project.html',{'projet':project, 'valide':valide, 'nameClient' : client, 'nameProfessionnel': professionnel, 'namePrestataire': prestataire, 'project_key': project.key, 'files' : documents_list_of_user_of_project})

        return render(request, 'project.html',{'projet':project, 'valide':valide, 'nameClient' : client, 'nameProfessionnel': professionnel, 'namePrestataire': prestataire, 'project_key': project.key, 'files' : sorted(documents_list_of_user_of_project, key=lambda files: files.upload_date, reverse=True)})
    else:
        valide = "Veuillez vous connecter pour voir cette page."
        return render(request, 'project.html',{'valide':valide})

def connected(request):
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
                        response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
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
	save = "False"
	if request.user.is_authenticated():
		if request.method == "POST" and 'new' in request.POST:
			form = ContractForm(request.POST)
			if form.is_valid():
				new_contract = form.save(commit=False)
				new_contract.projet_key = uidb32
				new_contract.created_date = timezone.now()
				new_contract.save()
				save = "True"
				return render(request, 'contract.html', {'contract':new_contract, 'save':save})
		elif request.method == "POST" and "edit" in request.POST:
			post = get_object_or_404(Contract, projet_key=uidb32)
			form = ContractForm(request.POST, instance=post)
			if form.is_valid():
				new_contract = form.save(commit=False)
				new_contract.projet_key = uidb32
				new_contract.created_date = timezone.now()
				new_contract.save()
				save = "True"
				return render(request, 'contract.html', {'contract':new_contract, 'save':save})	 
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
		else:
			form = ContractForm()
			user = CustomUser.objects.all()
			for i in user:
				if project.prestataire == i.email:
					prestataire = i.username
				if project.client == i.email:
					client = i.username
				if project.professionnel == i.email:
					professionnel = i.username
					
			if Projet.objects.filter(key=uidb32).exists():
				if Contract.objects.filter(projet_key=uidb32).exists():
					if request.user.typeUser ==prestataire :
						valide = "Vous n'avez pas accès à ce projet."
						return render(request, 'project.html',{'valide':valide})
					contract =  Contract.objects.get(projet_key=uidb32)
					return render(request, 'contract.html', {'contract':contract,'save':save})
				else:
					contract=""
					error = "Il n'y a pas encore de contrat pour ce projet."
					return render(request, 'contract.html',{'contract':contract ,'error':error, 'form':form})
			else:
				valide = "Le Projet n'existe pas."
				return render(request, 'project.html',{'valide':valide})
	else:
		valide = "Veuillez vous connecter pour voir cette page."
		return render(request, 'project.html',{'valide':valide})
