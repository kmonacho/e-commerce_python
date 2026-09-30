"""
Gestion des commandes. Les operations sensibles (passer commande, annuler)
sont executees dans une transaction manuelle (autocommit desactive le temps
de l'operation) afin de garantir la coherence entre commande, lignes de
commande et stock.
"""
from app.dao import panier_dao, taille_dao
from app.db import executer, obtenir_connexion, tous_les_resultats, un_resultat


def passer_commande(utilisateur_id):
    """
    Transforme le panier de l'utilisateur en commande EN_ATTENTE, decremente
    le stock de chaque taille commandee, puis vide le panier.
    Retourne l'id de la commande creee, ou None si le panier est vide ou le
    stock insuffisant (la transaction est alors annulee).
    """
    items = panier_dao.lister_par_utilisateur(utilisateur_id)
    if not items:
        return None

    conn = obtenir_connexion()
    conn.autocommit = False
    curseur = conn.cursor()
    try:
        total = sum(item["sous_total"] for item in items)

        curseur.execute(
            "INSERT INTO commande (utilisateur_id, statut, total) VALUES (%s, 'EN_ATTENTE', %s)",
            (utilisateur_id, total),
        )
        commande_id = curseur.lastrowid

        for item in items:
            curseur.execute(
                "UPDATE taille SET stock = stock - %s WHERE id = %s AND stock >= %s",
                (item["quantite"], item["taille_id"], item["quantite"]),
            )
            if curseur.rowcount != 1:
                conn.rollback()
                return None  # stock insuffisant

            curseur.execute(
                "INSERT INTO ligne_commande (commande_id, taille_id, quantite, prix_unitaire) "
                "VALUES (%s,%s,%s,%s)",
                (commande_id, item["taille_id"], item["quantite"], item["prix_unitaire"]),
            )

        curseur.execute("DELETE FROM panier_item WHERE utilisateur_id=%s", (utilisateur_id,))
        conn.commit()
        return commande_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.autocommit = True


def annuler_commande(commande_id, utilisateur_id):
    """Annule une commande EN_ATTENTE et restitue le stock correspondant."""
    commande = trouver_par_id(commande_id)
    if not commande or commande["utilisateur_id"] != utilisateur_id or commande["statut"] != "EN_ATTENTE":
        return False

    conn = obtenir_connexion()
    conn.autocommit = False
    curseur = conn.cursor()
    try:
        for ligne in commande["lignes"]:
            curseur.execute(
                "UPDATE taille SET stock = stock + %s WHERE id=%s",
                (ligne["quantite"], ligne["taille_id"]),
            )
        curseur.execute("UPDATE commande SET statut='ANNULEE' WHERE id=%s", (commande_id,))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.autocommit = True


def marquer_payee(commande_id, mode_paiement):
    curseur = executer(
        "UPDATE commande SET statut='PAYEE', mode_paiement=%s WHERE id=%s AND statut='EN_ATTENTE'",
        (mode_paiement, commande_id),
        commit=True,
    )
    return curseur.rowcount == 1


def _lister_lignes(commande_id):
    sql = """
        SELECT lc.*, c.modele, t.taille_us, t.taille_fr
        FROM ligne_commande lc
        JOIN taille t ON t.id = lc.taille_id
        JOIN chaussure c ON c.id = t.chaussure_id
        WHERE lc.commande_id = %s
    """
    return tous_les_resultats(sql, (commande_id,))


def trouver_par_id(commande_id):
    sql = """
        SELECT co.*, u.email FROM commande co
        JOIN utilisateur u ON u.id = co.utilisateur_id
        WHERE co.id = %s
    """
    commande = un_resultat(sql, (commande_id,))
    if commande:
        commande["lignes"] = _lister_lignes(commande_id)
    return commande


def lister_par_utilisateur(utilisateur_id):
    sql = """
        SELECT co.*, u.email FROM commande co
        JOIN utilisateur u ON u.id = co.utilisateur_id
        WHERE co.utilisateur_id = %s
        ORDER BY co.date_commande DESC
    """
    commandes = tous_les_resultats(sql, (utilisateur_id,))
    for commande in commandes:
        commande["lignes"] = _lister_lignes(commande["id"])
    return commandes


def lister_toutes():
    """Toutes les commandes, pour l'administrateur."""
    sql = """
        SELECT co.*, u.email FROM commande co
        JOIN utilisateur u ON u.id = co.utilisateur_id
        ORDER BY co.date_commande DESC
    """
    commandes = tous_les_resultats(sql)
    for commande in commandes:
        commande["lignes"] = _lister_lignes(commande["id"])
    return commandes
