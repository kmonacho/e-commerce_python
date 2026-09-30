# ShoeBoutique — E-commerce de chaussures (Python 3 / Flask / MySQL)

Version Python de la boutique en ligne, avec la même logique métier que la
version Java (JSP/Servlets) : Flask + Jinja2 côté web, MySQL 8.1 côté
données, sans ORM (requêtes SQL explicites via `mysql-connector-python`
pour garder un contrôle total, à la manière des DAO de la version Java).

## 1. Arborescence

```
boutique-python/
├── run.py                      -> point d'entrée (flask run / python run.py)
├── config.py                   -> configuration (lit .env)
├── requirements.txt
├── sql/schema.sql              -> création de la base + données de démo
├── scripts/creer_admin.py      -> création du premier compte administrateur
└── app/
    ├── __init__.py             -> application factory + enregistrement des blueprints
    ├── db.py                   -> connexion MySQL (pattern Flask "g")
    ├── security.py             -> hachage mot de passe + force du mot de passe
    ├── card_validator.py       -> Luhn + détection Visa/Mastercard
    ├── decorateurs.py          -> @connexion_requise, @admin_requis
    ├── dao/                    -> accès aux données (une fonction = une requête)
    ├── routes/                 -> blueprints Flask (public, auth, panier, commande, paiement, admin)
    ├── templates/              -> pages Jinja2 (+ admin/, commun/)
    └── static/css/style.css
```

## 2. Installation

```bash
cd boutique-python
python3 -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # puis adapte les identifiants MySQL dedans
```

## 3. Base de données

1. Démarrer MySQL 8.1.
2. Exécuter le script :
   ```bash
   mysql -u root -p < sql/schema.sql
   ```
   Il crée la base `boutique_chaussures`, toutes les tables (y compris
   `collection`, extensible depuis le back-office), et des données de
   démonstration (marques, 4 modèles avec tailles US/FR, 2 partenaires,
   2 codes de carte cadeau Google de test).
3. Vérifie/adapte les identifiants dans `.env` (`DB_HOST`, `DB_NAME`,
   `DB_USER`, `DB_PASSWORD`).

## 4. Créer le compte administrateur

Le mot de passe est haché (PBKDF2 via `werkzeug.security`) avant d'être
stocké, on ne peut donc pas insérer l'admin directement en SQL :

```bash
python scripts/creer_admin.py admin@boutique.com MotDePasse1!
```

Le compte est créé avec le rôle `ADMIN`.

## 5. Lancer le site

```bash
python run.py
```

Le site est accessible sur `http://localhost:5000/`.

Pour un usage plus proche de la production, tu peux aussi lancer :
```bash
flask --app run:application run
```
ou déployer derrière un vrai serveur WSGI (gunicorn, waitress) :
```bash
pip install gunicorn
gunicorn -w 4 "run:application"
```

## 6. Fonctionnalités livrées

- **Rubriques publiques** : Accueil, Femmes, Hommes, Partenaires, Contact.
- **Chaussures** : modèle, marque, date de sortie, prix, tailles US **et**
  FR par modèle avec stock, collection initialisée sur `Aucune` par défaut
  — et l'administrateur peut **ajouter de nouvelles collections** depuis
  `/admin/collections`.
- **Compte client** : inscription, connexion (session Flask signée côté
  client), déconnexion. Mot de passe haché avec PBKDF2 (werkzeug), jamais
  stocké en clair.
- **Indicateur de force du mot de passe**, affiché en direct en JS sur le
  formulaire d'inscription et revérifié côté serveur
  (`app/security.py::evaluer_force`), basé sur 3 critères : présence d'un
  chiffre, d'une majuscule, d'un caractère spécial (en plus du minimum de
  8 caractères obligatoire).
- **Consentement cookies** : case à cocher lors de l'inscription/connexion,
  et bandeau persistant (`/api/cookies`) si aucun choix n'a encore été fait.
- **Panier** : protégé par le décorateur `@connexion_requise`, ajout,
  suppression d'articles.
- **Commande** : transformation du panier en commande (transaction SQL avec
  décrémentation atomique du stock), annulation (restitue le stock),
  historique client.
- **Paiement**, 3 moyens :
  - **Carte bancaire** : `card_validator.py` vérifie l'algorithme de Luhn
    **et** le préfixe/la longueur pour confirmer qu'il s'agit bien d'une
    carte **Visa** ou **Mastercard**, plus la date d'expiration et le CVV.
  - **TWINT** : simulation via un numéro de téléphone suisse.
  - **Carte cadeau Google** : vérification du code et du solde en base
    (table `carte_cadeau_google`).
- **Back-office administrateur** (`/admin/*`, protégé par `@admin_requis`) :
  tableau de bord, CRUD des modèles de chaussures, gestion des tailles/stock
  par modèle, gestion des collections (ajout de nouvelles collections),
  ajout de partenaires, consultation de toutes les commandes, lecture des
  messages du formulaire de contact.

## 7. Numéros de carte de test (algorithme de Luhn valide)

- Visa : `4111 1111 1111 1111`
- Mastercard : `5500 0000 0000 0004`

Ces numéros sont des numéros de test standards ; aucune passerelle de
paiement externe n'est appelée dans ce projet, tout est simulé côté serveur.

## 8. Sécurité — pistes d'amélioration pour une mise en production réelle

Ce projet est pédagogique. Avant une mise en production, il faudrait a
minima :
- passer les identifiants MySQL et `SECRET_KEY` en vraies variables
  d'environnement (déjà externalisées via `.env`, mais à ne jamais commiter),
- ajouter une protection CSRF sur les formulaires (ex. `Flask-WTF`),
- utiliser des sessions côté serveur (ex. `Flask-Session` + Redis) plutôt
  que le cookie de session signé par défaut, pour les données sensibles,
- brancher de vraies passerelles de paiement (Stripe/Saferpay pour les
  cartes, l'API officielle TWINT, l'API Google Play/Wallet pour les cartes
  cadeaux) plutôt que la simulation actuelle,
- forcer HTTPS et le flag `Secure` sur les cookies
  (`SESSION_COOKIE_SECURE = True` en production).
