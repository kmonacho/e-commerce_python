from app.db import executer, tous_les_resultats, un_resultat


def lister_tailles_par_chaussure(chaussure_id):
    return tous_les_resultats(
        "SELECT * FROM taille WHERE chaussure_id=%s ORDER BY taille_us", (chaussure_id,)
    )


def trouver_par_id(taille_id):
    return un_resultat("SELECT * FROM taille WHERE id=%s", (taille_id,))


def ajouter(chaussure_id, taille_us, taille_fr, stock):
    sql = "INSERT INTO taille (chaussure_id, taille_us, taille_fr, stock) VALUES (%s,%s,%s,%s)"
    curseur = executer(sql, (chaussure_id, taille_us, taille_fr, stock), commit=True)
    return curseur.lastrowid


def modifier_stock(taille_id, nouveau_stock):
    executer("UPDATE taille SET stock=%s WHERE id=%s", (nouveau_stock, taille_id), commit=True)


def decrementer_stock(taille_id, quantite):
    """
    Decremente le stock de maniere atomique (utilise dans une transaction de commande).
    Retourne True si l'operation a reussi (stock suffisant), False sinon.
    """
    from app.db import obtenir_connexion

    conn = obtenir_connexion()
    curseur = conn.cursor()
    curseur.execute(
        "UPDATE taille SET stock = stock - %s WHERE id = %s AND stock >= %s",
        (quantite, taille_id, quantite),
    )
    return curseur.rowcount == 1


def incrementer_stock(taille_id, quantite):
    executer("UPDATE taille SET stock = stock + %s WHERE id=%s", (quantite, taille_id), commit=True)


def supprimer(taille_id):
    executer("DELETE FROM taille WHERE id=%s", (taille_id,), commit=True)
