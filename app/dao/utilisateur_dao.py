from app.db import executer, un_resultat


def trouver_par_email(email):
    return un_resultat("SELECT * FROM utilisateur WHERE email=%s", (email,))


def trouver_par_id(utilisateur_id):
    return un_resultat("SELECT * FROM utilisateur WHERE id=%s", (utilisateur_id,))


def email_existe(email):
    return trouver_par_email(email) is not None


def creer(nom, prenom, email, mot_de_passe_hash, role="CLIENT", accepte_cookies=False):
    sql = """
        INSERT INTO utilisateur (nom, prenom, email, mot_de_passe_hash, role, accepte_cookies)
        VALUES (%s,%s,%s,%s,%s,%s)
    """
    curseur = executer(sql, (nom, prenom, email, mot_de_passe_hash, role, accepte_cookies), commit=True)
    return curseur.lastrowid
