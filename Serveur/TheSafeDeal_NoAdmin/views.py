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



# Create your views here.

def about(request):
    return render(request, 'about.html', {})

def home(request):
    return render(request, 'home.html', {})

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
    if request.method == "POST":
        form = NewProjectForm(request.POST)

        if form.is_valid(): 
            cleaned_info = form.cleaned_data
            new_project = form.save(commit=False)
            new_project.key = get_random_string(length=32)
            new_project.date_debut = timezone.now()

            if User.objects.filter(email = cleaned_info['prestataire']).exists() and User.objects.filter(email = cleaned_info['professionnel']).exists():
                if cleaned_info['client'] == '':
                    new_project.save()
                    pre = UserProfile.objects.get(email = cleaned_info['prestataire'])
                    pre.add_project(new_project.key)
                    pre.save()
                    pro = UserProfile.objects.get(email = cleaned_info['professionnel'])
                    pro.add_project(new_project.key)
                    pro.save()
                else:
                    if User.objects.filter(email = cleaned_info['client']).exists():
                        new_project.save()
                        UserProfile.objects.filter(email = cleaned_info['prestataire']).add_project(new_project.key)
                        UserProfile.objects.filter(email = cleaned_info['professionnel']).add_project(new_project.key)
                        UserProfile.objects.filter(email = cleaned_info['client']).add_project(new_project.key)
                    else:
                        error = "Le Client n'est pas enregistré à cette adresse mail, veuillez recréer le projet."
                        return render(request, 'connected.html',{'form':form, 'error': error})
            else:
                if not User.objects.filter(email = cleaned_info['prestataire']).exists():
                    error = "Le Prestataire n'est pas enregistré à cette adresse mail, veuillez recréer le projet."
                elif not User.objects.filter(email = cleaned_info['professionnel']).exists():
                    error = "Le Professionnel n'est pas enregistré à cette adresse mail, veuillez recréer le projet."
                return render(request, 'connected.html',{'form':form, 'error': error})
    else:
        form = NewProjectForm()

    return render(request, 'connected.html',{'form':form, 'user':request.user})
