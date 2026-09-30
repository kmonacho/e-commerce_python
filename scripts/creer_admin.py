"""
Script en ligne de commande pour creer le premier compte administrateur.
Le mot de passe doit etre hache correctement (PBKDF2 via werkzeug), on ne
peut donc pas l'inserer directement en SQL brut.

Utilisation (depuis la racine du projet) :
    python scripts/creer_admin.py admin@boutique.com MotDePasse1!
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import creer_application
from app.dao import utilisateur_dao
from app.security import hacher_mot_de_passe, longueur_valide


def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/creer_admin.py <email> <mot_de_passe>")
        sys.exit(1)

    email = sys.argv[1]
    mot_de_passe = sys.argv[2]

    if not longueur_valide(mot_de_passe):
        print("Le mot de passe doit contenir au moins 8 caracteres.")
        sys.exit(1)

    app = creer_application()
    with app.app_context():
        if utilisateur_dao.email_existe(email):
            print(f"Un compte existe deja avec l'email {email}.")
            sys.exit(1)

        hash_mdp = hacher_mot_de_passe(mot_de_passe)
        utilisateur_dao.creer("Admin", "Boutique", email, hash_mdp, role="ADMIN", accepte_cookies=True)
        print(f"Administrateur cree avec succes : {email}")


if __name__ == "__main__":
    main()
