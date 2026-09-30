from app.db import executer, tous_les_resultats, un_resultat

_SELECT_BASE = """
    SELECT p.id, p.utilisateur_id, p.taille_id, p.quantite,
           c.modele, m.nom AS nom_marque, t.taille_us, t.taille_fr, c.prix AS prix_unitaire
    FROM panier_item p
    JOIN taille t ON t.id = p.taille_id
    JOIN chaussure c ON c.id = t.chaussure_id
    JOIN marque m ON m.id = c.marque_id
    WHERE p.utilisateur_id = %s
"""


def lister_par_utilisateur(utilisateur_id):
    items = tous_les_resultats(_SELECT_BASE, (utilisateur_id,))
    for item in items:
        item["sous_total"] = float(item["prix_unitaire"]) * item["quantite"]
    return items


def ajouter_ou_incrementer(utilisateur_id, taille_id, quantite):
    existant = un_resultat(
        "SELECT id, quantite FROM panier_item WHERE utilisateur_id=%s AND taille_id=%s",
        (utilisateur_id, taille_id),
    )
    if existant:
        executer(
            "UPDATE panier_item SET quantite=%s WHERE id=%s",
            (existant["quantite"] + quantite, existant["id"]),
            commit=True,
        )
    else:
        executer(
            "INSERT INTO panier_item (utilisateur_id, taille_id, quantite) VALUES (%s,%s,%s)",
            (utilisateur_id, taille_id, quantite),
            commit=True,
        )


def supprimer_item(item_id, utilisateur_id):
    executer(
        "DELETE FROM panier_item WHERE id=%s AND utilisateur_id=%s",
        (item_id, utilisateur_id),
        commit=True,
    )


def vider_panier(utilisateur_id):
    executer("DELETE FROM panier_item WHERE utilisateur_id=%s", (utilisateur_id,), commit=True)
