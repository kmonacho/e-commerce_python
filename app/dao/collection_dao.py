from app.db import executer, tous_les_resultats


def lister_toutes():
    return tous_les_resultats("SELECT * FROM collection ORDER BY nom")


def creer(nom):
    """Permet a l'administrateur de reajouter/creer une nouvelle collection."""
    curseur = executer("INSERT INTO collection (nom) VALUES (%s)", (nom,), commit=True)
    return curseur.lastrowid
