from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User


# Create your models here.

TYPE_USER = (
	('Prestataire', 'Prestataire'),
	('Professionnel', 'Professionnel'),
	('Client', 'Client')
)

class CustomUser(AbstractUser):
    typeUser = models.CharField(max_length=30, choices=TYPE_USER,null=False, blank=False)

    
class Projet(models.Model):
	titre = models.CharField(max_length=200)
	key = models.CharField(max_length=32, unique=True)
	prestataire = models.TextField(max_length=150)
	client = models.TextField(max_length=150, blank=True)
	professionnel = models.TextField(max_length=150)
	date_debut = models.DateTimeField(auto_now_add = True)
	date_fin = models.DateTimeField(auto_now = False, blank = False)
	description = models.TextField()
	prix = models.DecimalField(max_digits=9, decimal_places=2)


	REQUIERED_FIELDS = []

	def __str__(self):
		return self.titre


