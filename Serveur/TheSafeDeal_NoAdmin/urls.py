from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^about$', views.about, name='about'),
    url(r'^login$', auth_views.login, {'template_name': 'login.html'},name='login'),
    url(r'^logout$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^register$', views.register, name='register'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',views.activate, name='activate'),
    url(r'^connected$', views.connected, name='connected'),
    url(r'^project/(?P<uidb32>[0-9A-Za-z_\-]+)/contract$', views.contract, name='contract'),
    url(r'^upload$', views.simple_upload, name='simple_upload'),
    url(r'^download/(?P<project_key>[0-9A-Za-z_\-]+)/(?P<document_key>[0-9A-Za-z_\-]+)$', views.download, name='download'),
	url(r'^project/(?P<uidb32>[0-9A-Za-z_\-]+)$', views.showProject, name='project'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)