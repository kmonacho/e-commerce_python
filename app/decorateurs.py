"""Decorateurs de controle d'acces : connexion requise / role administrateur requis."""
from functools import wraps

from flask import abort, flash, redirect, session, url_for, request


def connexion_requise(vue):
    @wraps(vue)
    def enveloppe(*args, **kwargs):
        if "utilisateur_id" not in session:
            flash("Vous devez vous connecter pour acceder a votre panier.", "erreur")
            session["apres_connexion"] = request.path
            return redirect(url_for("auth.connexion"))
        return vue(*args, **kwargs)
    return enveloppe


def admin_requis(vue):
    @wraps(vue)
    def enveloppe(*args, **kwargs):
        if "utilisateur_id" not in session:
            return redirect(url_for("auth.connexion"))
        if session.get("role") != "ADMIN":
            abort(403)
        return vue(*args, **kwargs)
    return enveloppe
