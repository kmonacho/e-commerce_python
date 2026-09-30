from app.db import executer, tous_les_resultats


def creer(nom, email, sujet, message):
    sql = "INSERT INTO message_contact (nom, email, sujet, message) VALUES (%s,%s,%s,%s)"
    curseur = executer(sql, (nom, email, sujet, message), commit=True)
    return curseur.lastrowid


def lister_tous():
    return tous_les_resultats("SELECT * FROM message_contact ORDER BY date_envoi DESC")


def marquer_lu(message_id):
    executer("UPDATE message_contact SET lu=TRUE WHERE id=%s", (message_id,), commit=True)
