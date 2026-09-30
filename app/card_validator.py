"""
Validation d'un numero de carte bancaire :
- algorithme de Luhn (cle de controle)
- detection du type (VISA / MASTERCARD) via le prefixe et la longueur
"""
import re
from datetime import date


def _nettoyer(numero: str) -> str:
    return re.sub(r"[^0-9]", "", numero or "")


def luhn_valide(numero_brut: str) -> bool:
    """Algorithme de Luhn : verifie la cle de controle du numero de carte."""
    numero = _nettoyer(numero_brut)
    if len(numero) < 12:
        return False

    somme = 0
    doubler = False
    for chiffre_car in reversed(numero):
        chiffre = int(chiffre_car)
        if doubler:
            chiffre *= 2
            if chiffre > 9:
                chiffre -= 9
        somme += chiffre
        doubler = not doubler
    return somme % 10 == 0


def determiner_type(numero_brut: str) -> str:
    """Retourne 'VISA', 'MASTERCARD' ou 'INCONNU' selon le prefixe (IIN) et la longueur."""
    numero = _nettoyer(numero_brut)

    # VISA : commence par 4, longueur 13, 16 ou 19
    if re.match(r"^4[0-9]{12}([0-9]{3})?([0-9]{3})?$", numero):
        return "VISA"

    # MASTERCARD : 51-55xxxx (16 chiffres) ou 2221-2720xxxx (nouvelle plage)
    if re.match(r"^5[1-5][0-9]{14}$", numero):
        return "MASTERCARD"

    if len(numero) == 16:
        prefixe4 = int(numero[:4])
        if 2221 <= prefixe4 <= 2720:
            return "MASTERCARD"

    return "INCONNU"


def carte_valide(numero: str) -> bool:
    """Une carte est acceptee si elle passe Luhn ET correspond a Visa ou Mastercard."""
    return luhn_valide(numero) and determiner_type(numero) != "INCONNU"


def date_expiration_valide(mois_str: str, annee_str: str) -> bool:
    """Validation basique de la date d'expiration au format MM/AA."""
    try:
        mois = int(mois_str)
        annee = int(annee_str)
        if annee < 100:
            annee += 2000
        if mois < 1 or mois > 12:
            return False
        aujourd_hui = date.today()
        # Carte valide jusqu'au dernier jour du mois d'expiration
        return (annee, mois) >= (aujourd_hui.year, aujourd_hui.month)
    except (ValueError, TypeError):
        return False


def cvv_valide(cvv: str) -> bool:
    return bool(cvv) and re.match(r"^[0-9]{3,4}$", cvv) is not None
