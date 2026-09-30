from app.db import executer, tous_les_resultats


def lister_tous():
    return tous_les_resultats("SELECT * FROM partenaire ORDER BY nom")


def creer(nom, description, logo_url, site_web):
    sql = "INSERT INTO partenaire (nom, description, logo_url, site_web) VALUES (%s,%s,%s,%s)"
    curseur = executer(sql, (nom, description, logo_url, site_web), commit=True)
    return curseur.lastrowid


def supprimer(partenaire_id):
    executer("DELETE FROM partenaire WHERE id=%s", (partenaire_id,), commit=True)
