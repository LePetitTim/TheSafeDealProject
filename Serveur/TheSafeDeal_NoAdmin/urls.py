from django.conf.urls import url
from . import views
from django.contrib.auth.views import LoginView

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^about$', views.about, name='about'),
    url(r'^login$', LoginView.as_view(template_name='login.html'),name='login'),
    url(r'^register$', views.register, name='register'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',views.activate, name='activate'),
]