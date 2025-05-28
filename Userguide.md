# Guide d'utilisation 
## Sommaire : 
1. Introduction
2. Installation de l’application
3. Présentation des rôles utilisateurs
4. Utilisation de l’application
5. Foire aux questions (FAQ) / Dépannage
### 1. Introduction 
### 2. Installation de l’application

#### 2.1 Configuration préalable

Avant d’installer l’application, il est nécessaire de configurer la base de données.
Nous utilisons Supabase comme service de base de données.
 Voici les étapes à suivre :
1. Créer un compte Supabase, si ce n’est pas déjà fait.
2. Créer un nouveau projet Supabase.
4. Importer le fichier bdd.sql pour initialiser la structure de la base de données.
6. Insérer les données des étudiants et des enseignants, car nous considérons qu’ils sont déjà inscrits dans le système.

Une fois la base de données configurée, vous pouvez installer l’application en suivant ces étapes :

Téléchargez l’application depuis ce lien : [lien à insérer].

Décompressez l’archive puis ouvrez le dossier dans Visual Studio Code (VS Code).

- Pour lancer le frontend :

Ouvrez un terminal dans VS Code.

Accédez au dossier front avec la commande : cd front
Installez les dépendances avec : npm install
Puis lancez l’application en exécutant : npm run dev

- Pour lancer le backend :

Ouvrez un second terminal .

Accédez au dossier back : cd back
Installez les dépendances Python avec : pip install [si nécessaire, insérer un module spécifique]
pip install -r requirements.txt
Lancez ensuite le serveur avec : py run.py

### 3. Présentation des rôles utilisateurs
L’application comporte deux rôles principaux : un pour les étudiants et un autre pour les enseignants.
Les comptes sont déjà créés dans la base de données. Pour différencier un étudiant d’un enseignant, on récupère l’adresse e-mail lors de la connexion, puis on la compare aux e-mails enregistrés dans la base, qui se trouvent dans deux tables distinctes : une pour les professeurs et une pour les étudiants. Selon le rôle déterminé, on redirige l’utilisateur vers sa page.

Le compte étudiant permet de se connecter et offre un menu avec deux options : remplir un formulaire (Form)ou consulter les résultats(Results).
Dans la page formulaire, l’étudiant voit une liste d’étudiants parmi lesquels il doit choisir. Il doit attribuer des points de préférence à chaque étudiant sélectionné. Si la somme des points n’atteint pas 100, une nouvelle liste s’affiche pour continuer à choisir des étudiants jusqu’à ce que le total fasse 100 points, que ce soit réparti entre plusieurs étudiants ou attribué à un seul. Ensuite, l’étudiant peut consulter ses résultats pour savoir dans quel groupe il a été placé.

Après connexion, les enseignants ont accès à plusieurs pages : une page de gestion des formulaires qui comprend un champ pour définir une date limite, un compteur affichant le nombre d’étudiants ayant répondu, un bouton pour fermer la session, ainsi qu’une case à cocher pour publier le formulaire ; une autre page permet de générer les résultats en précisant le nombre d’étudiants par groupe (paramètre n) ; enfin, une dernière page offre la possibilité de visualiser tous les groupes formés.







