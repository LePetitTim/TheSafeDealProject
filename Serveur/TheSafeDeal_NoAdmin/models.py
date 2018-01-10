from django.db import models
from django.contrib.auth.models import AbstractUser

TYPE_USER = (
	('Prestataire', 'Prestataire'),
	('Professionnel', 'Professionnel'),
	('Client', 'Client')
)

class CustomUser(AbstractUser):
    typeUser = models.CharField(max_length=30, choices=TYPE_USER,null=False, blank=False)