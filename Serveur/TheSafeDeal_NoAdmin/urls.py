from django.conf.urls import url, include
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings


"""
Patterns pour la redirection des vues. Lorsque vous obtenez l'url https://<domaine>, vous arrivez sur la vue home.
La vue home va ensuite diriger sur la page home.
De même pour tous les urls.
"""
urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^about$', views.about, name='about'),
    url(r'^login$', auth_views.login, {'template_name': 'login.html'},name='login'),
    url(r'^logout$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^register$', views.register, name='register'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',views.activate, name='activate'),
    url(r'^connected$', views.connected, name='connected'),
    url(r'^project/(?P<uidb32>[0-9A-Za-z_\-]+)/contract$', views.contract, name='contract'),
    url(r'^download/(?P<project_key>[0-9A-Za-z_\-]+)/(?P<document_key>[0-9A-Za-z_\-]+)$', views.download, name='download'),
	url(r'^project/(?P<uidb32>[0-9A-Za-z_\-]+)$', views.showProject, name='project'),
	url(r'^api-token/', views.api_token, name='api_token'),
]

"""
Utilisé pour la gestion des fichiers et permet de télécharger les differents fichiers dans la racine des medias.
"""
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)