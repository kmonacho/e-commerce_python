from app.db import executer


def enregistrer(commande_id, mode, reference, reussi):
    sql = "INSERT INTO paiement (commande_id, mode, reference, statut) VALUES (%s,%s,%s,%s)"
    executer(sql, (commande_id, mode, reference, "REUSSI" if reussi else "ECHOUE"), commit=True)
