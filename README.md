# TheSafeDealProject
Projet ISEN de Janvier 2018 - M2

Prérequis : Python3

--------------------------------------------------------------------

Installation du Serveur :

Dans le dossier d'origine : 
>$ git clone https://github.com/LePetitTim/TheSafeDealProject.git

Supprimer db.sqlite3 qui se trouve dans le répertoire TheSafeDealProject/Serveur.

Aller dans <Dossier d'origine>/TheSafeDealProject/Serveur :
>$ cd TheSafeDealProject
>$ cd Serveur

Activer l'environnement myvenv : 
>$ myvenv\Scripts\activate

Vous devriez voir un "(myvenv)" apparaître à côté du chemin dans le terminal : vous êtes bien dans votre environnement virtuel.
Il permet d'installer des modules ou autres outils séparement de votre environnement Python global.

Installation de Django : 
>$ python.exe -m pip install django~=1.11.0

Installation du module Corsheaders :
>$ python.exe -m pip install django-cors-headers

Lancer la commande
>$ python manage.py makemigrations TheSafeDeal_NoAdmin

Lancer la commande 
>$ python manage.py migrate TheSafeDeal_NoAdmin

Vous devez normalement avoir un nouveau db.sqlite3 vierge dans TheSafeDealProject/Serveur.

Vous pouvez désormais démarrer le serveur en utilisant la commande : 
>$ python manage.py runserver

/!\ Si vous utilisez Windows et que vous obtenez l'erreur UnicodeDecodeError, tapez plutôt cette commande : 
>$ python manage.py runserver 0:8000

Vous pouvez désormais vous connecter au serveur sur http://127.0.0.8:8000 si vous n'avez pas changé le host dans TheSafeDeal/settings.py

Le serveur est hébergé en LOCAL uniquement.
Pour héberger le serveur et le rendre accessible à votre réseau, il vous faut ajouter votre adresse IP dans les "ALLOWED_HOSTS" du fichier TheSafeDeal/settings.py, ligne 30. Si votre adresse IP est '192.168.1.16', vous obtenez quelque chose comme :
> ALLOWED_HOSTS = ["127.0.0.1","192.168.1.16"]

Enregistrez votre modification et relancez le serveur avec cette commande :
>$ python manage.py runserver 0.0.0.0:8000

Et voilà! Votre serveur est accessible pour toutes les personnes connectées à votre réseau à l'adresse http://192.168.1.16:8000
Si vous n'arrivez pas à vous connecter au serveur en réseau vérifiez que votre parefeu autorise bien l'application.