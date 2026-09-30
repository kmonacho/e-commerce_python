"""
Gestion de la connexion MySQL. Une connexion par requete HTTP est ouverte
puis refermee automatiquement (pattern Flask 'g' + teardown_appcontext).
"""
import mysql.connector
from flask import current_app, g


def obtenir_connexion():
    if "db" not in g:
        g.db = mysql.connector.connect(
            host=current_app.config["DB_HOST"],
            port=current_app.config["DB_PORT"],
            database=current_app.config["DB_NAME"],
            user=current_app.config["DB_USER"],
            password=current_app.config["DB_PASSWORD"],
            autocommit=True,
        )
    return g.db


def fermer_connexion_bd(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def executer(sql, params=None, commit=False):
    """Execute une requete (INSERT/UPDATE/DELETE) et retourne le curseur."""
    conn = obtenir_connexion()
    curseur = conn.cursor(dictionary=True)
    curseur.execute(sql, params or ())
    if commit:
        conn.commit()
    return curseur


def un_resultat(sql, params=None):
    curseur = executer(sql, params)
    return curseur.fetchone()


def tous_les_resultats(sql, params=None):
    curseur = executer(sql, params)
    return curseur.fetchall()
