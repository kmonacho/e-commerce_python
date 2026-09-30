from app.db import executer, un_resultat


def solde(code):
    """Retourne le montant de la carte si le code existe et n'a pas encore ete utilise, sinon None."""
    ligne = un_resultat(
        "SELECT montant FROM carte_cadeau_google WHERE code=%s AND utilisee=FALSE", (code,)
    )
    return float(ligne["montant"]) if ligne else None


def utiliser(code, montant_requis):
    """Marque la carte comme utilisee si son solde couvre le montant demande."""
    disponible = solde(code)
    if disponible is None or disponible < montant_requis:
        return False
    curseur = executer(
        "UPDATE carte_cadeau_google SET utilisee=TRUE WHERE code=%s AND utilisee=FALSE",
        (code,),
        commit=True,
    )
    return curseur.rowcount == 1
