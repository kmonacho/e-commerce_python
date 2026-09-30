from app.db import executer, tous_les_resultats


def lister_toutes():
    return tous_les_resultats("SELECT * FROM marque ORDER BY nom")


def creer(nom):
    curseur = executer("INSERT INTO marque (nom) VALUES (%s)", (nom,), commit=True)
    return curseur.lastrowid
