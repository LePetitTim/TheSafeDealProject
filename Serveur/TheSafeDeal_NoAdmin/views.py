from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignupForm
from .forms import NewProjectForm
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
from .models import CustomUser

# Create your views here.

def about(request):
    return render(request, 'about.html', {})

def home(request):
    customUser = CustomUser.objects.all()
    return render(request, 'home.html', {'CustomUser' : customUser})

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

                if CustomUser.objects.filter(email = cleaned_info['client']).exists() and CustomUser.objects.filter(email = cleaned_info['professionnel']).exists():
                    if cleaned_info['prestataire'] == '':
                        cli = CustomUser.objects.get(email = cleaned_info['client'])
                        pro = CustomUser.objects.get(email = cleaned_info['professionnel'])
                        if cli.typeUser == 'Client' and pro.typeUser == 'Professionnel':
                            new_project.save()
                            cli.add_project(new_project.key)
                            cli.save()
                            pro.add_project(new_project.key)
                            pro.save()
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
                                pre.save()
                                pro.add_project(new_project.key)
                                pro.save()
                                cli.add_project(new_project.key)
                                cli.save()
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
            #request.META['QUERY_STRING'] = ''
        else:
            form = NewProjectForm()
        return render(request, 'connected.html',{'form':form, 'user':request.user, 'validated_projects':validated_projects, 'unvalidated_projects':unvalidated_projects})
    else:
        form = NewProjectForm()

    return render(request, 'connected.html',{'form':form, 'user':request.user})


