from app.db import executer, tous_les_resultats, un_resultat
from app.dao.taille_dao import lister_tailles_par_chaussure

_SELECT_BASE = """
    SELECT c.id, c.modele, c.marque_id, m.nom AS nom_marque, c.date_sortie, c.prix,
           c.genre, c.collection_id, col.nom AS nom_collection, c.description, c.image_url
    FROM chaussure c
    JOIN marque m ON m.id = c.marque_id
    JOIN collection col ON col.id = c.collection_id
"""


def lister_toutes():
    return tous_les_resultats(_SELECT_BASE + " ORDER BY c.id DESC")


def lister_par_genre(genre):
    sql = _SELECT_BASE + " WHERE c.genre = %s OR c.genre = 'UNISEXE' ORDER BY c.id DESC"
    return tous_les_resultats(sql, (genre,))


def trouver_par_id(chaussure_id):
    chaussure = un_resultat(_SELECT_BASE + " WHERE c.id = %s", (chaussure_id,))
    if chaussure:
        chaussure["tailles"] = lister_tailles_par_chaussure(chaussure_id)
    return chaussure


def creer(donnees):
    sql = """
        INSERT INTO chaussure (modele, marque_id, date_sortie, prix, genre, collection_id, description, image_url)
        VALUES (%(modele)s, %(marque_id)s, %(date_sortie)s, %(prix)s, %(genre)s, %(collection_id)s, %(description)s, %(image_url)s)
    """
    curseur = executer(sql, donnees, commit=True)
    return curseur.lastrowid


def modifier(chaussure_id, donnees):
    sql = """
        UPDATE chaussure SET modele=%(modele)s, marque_id=%(marque_id)s, date_sortie=%(date_sortie)s,
               prix=%(prix)s, genre=%(genre)s, collection_id=%(collection_id)s,
               description=%(description)s, image_url=%(image_url)s
        WHERE id=%(id)s
    """
    donnees = {**donnees, "id": chaussure_id}
    executer(sql, donnees, commit=True)


def supprimer(chaussure_id):
    executer("DELETE FROM chaussure WHERE id=%s", (chaussure_id,), commit=True)
