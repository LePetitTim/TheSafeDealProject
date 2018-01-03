from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^about$', views.about, name='about'),
    url(r'^login$', views.login, name='login'),
    url(r'^$', views.home, name='home'),
]