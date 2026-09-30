"""
Hachage du mot de passe (PBKDF2 via werkzeug, deja fourni avec Flask) et
evaluation de la force du mot de passe selon 3 criteres :
1. presence d'un chiffre, 2. presence d'une majuscule, 3. caractere special.
"""
import re

from werkzeug.security import check_password_hash, generate_password_hash


def hacher_mot_de_passe(mot_de_passe: str) -> str:
    return generate_password_hash(mot_de_passe)


def verifier_mot_de_passe(mot_de_passe_saisi: str, hash_stocke: str) -> bool:
    return check_password_hash(hash_stocke, mot_de_passe_saisi)


def longueur_valide(mdp: str) -> bool:
    return bool(mdp) and len(mdp) >= 8


def contient_chiffre(mdp: str) -> bool:
    return bool(mdp) and re.search(r"[0-9]", mdp) is not None


def contient_majuscule(mdp: str) -> bool:
    return bool(mdp) and re.search(r"[A-Z]", mdp) is not None


def contient_caractere_special(mdp: str) -> bool:
    return bool(mdp) and re.search(r"[^a-zA-Z0-9]", mdp) is not None


def evaluer_force(mdp: str) -> dict:
    """
    Retourne un dict avec le detail des 3 criteres et un libelle de force,
    utilise a la fois par le formulaire d'inscription (validation serveur)
    et par l'endpoint AJAX /api/force-mot-de-passe (retour visuel instantane).
    """
    chiffre = contient_chiffre(mdp)
    majuscule = contient_majuscule(mdp)
    special = contient_caractere_special(mdp)
    longueur_ok = longueur_valide(mdp)

    score = sum([chiffre, majuscule, special])

    if not longueur_ok:
        libelle = "Trop court (8 caracteres minimum)"
    elif score == 0:
        libelle = "Faible"
    elif score == 1:
        libelle = "Moyen"
    elif score == 2:
        libelle = "Fort"
    else:
        libelle = "Tres fort"

    return {
        "score": score,
        "libelle": libelle,
        "longueur_valide": longueur_ok,
        "chiffre": chiffre,
        "majuscule": majuscule,
        "special": special,
    }
