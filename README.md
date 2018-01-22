# TheSafeDealProject
Project January 2018

Pour l'instalation du Serveur :

Dans le dossier d'origine : git clone https://github.com/LePetitTim/TheSafeDealProject.git

Aller dans <Dossier d'origine>/TheSafeDealProject/Serveur

Supprimer db.sqlite3

Activer l'environnement myvenv : myvenv\Scripts\activate

Lancer la commande python manage.py makemigrations TheSafeDealProject_NoAdmin

Lancer la commande python manage.py migrate TheSafeDealProject_NoAdmin

Vous devez normalement avoir un nouveau db.sqlite3 vierge.

Vous pouvez desormais demarrer le serveur en utilisant la commande : python manage.py runserver
/!\ Si vous utilisez Windows et que vous obtenez l'erreur UnicodeDecodeError, tapez plutôt cette commande : python manage.py runserver 0:8000

Vous pouvez desormais vous conecter au serveur sur 127.0.0.8 si vous n'avez pas changé le host dans TheSafeDeal/settings.py
