from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for

from app.dao import utilisateur_dao
from app.security import (
    evaluer_force,
    hacher_mot_de_passe,
    longueur_valide,
    verifier_mot_de_passe,
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/inscription", methods=["GET", "POST"])
def inscription():
    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        prenom = request.form.get("prenom", "").strip()
        email = request.form.get("email", "").strip().lower()
        mot_de_passe = request.form.get("mot_de_passe", "")
        confirmation = request.form.get("confirmation", "")
        accepte_cookies = request.form.get("accepte_cookies") == "on"

        contexte = {"nom": nom, "prenom": prenom, "email": email}

        if not nom or not prenom or not email or "@" not in email:
            return render_template("inscription.html", erreur="Merci de renseigner correctement tous les champs.", **contexte)
        if not longueur_valide(mot_de_passe):
            return render_template("inscription.html", erreur="Le mot de passe doit contenir au moins 8 caracteres.", **contexte)
        if mot_de_passe != confirmation:
            return render_template("inscription.html", erreur="Les deux mots de passe ne correspondent pas.", **contexte)
        if utilisateur_dao.email_existe(email):
            return render_template("inscription.html", erreur="Un compte existe deja avec cet email.", **contexte)

        hash_mdp = hacher_mot_de_passe(mot_de_passe)
        utilisateur_dao.creer(nom, prenom, email, hash_mdp, role="CLIENT", accepte_cookies=accepte_cookies)

        flash("Compte cree avec succes, vous pouvez vous connecter.", "succes")
        reponse = redirect(url_for("auth.connexion"))
        if accepte_cookies:
            reponse.set_cookie("cookies_acceptes", "true", max_age=60 * 60 * 24 * 365)
        return reponse

    return render_template("inscription.html")


@auth_bp.route("/api/force-mot-de-passe", methods=["POST"])
def api_force_mot_de_passe():
    """Endpoint AJAX (facultatif, la verification est deja faite en JS cote client
    et systematiquement revalidee cote serveur a l'inscription)."""
    mdp = request.form.get("mot_de_passe", "")
    return jsonify(evaluer_force(mdp))


@auth_bp.route("/connexion", methods=["GET", "POST"])
def connexion():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        mot_de_passe = request.form.get("mot_de_passe", "")
        accepte_cookies = request.form.get("accepte_cookies") == "on"

        utilisateur = utilisateur_dao.trouver_par_email(email)
        if not utilisateur or not verifier_mot_de_passe(mot_de_passe, utilisateur["mot_de_passe_hash"]):
            return render_template("connexion.html", erreur="Email ou mot de passe incorrect.", email=email)

        session.clear()
        session["utilisateur_id"] = utilisateur["id"]
        session["prenom"] = utilisateur["prenom"]
        session["role"] = utilisateur["role"]

        apres_connexion = session.pop("apres_connexion", None)

        if utilisateur["role"] == "ADMIN":
            destination = url_for("admin.tableau_de_bord")
        elif apres_connexion:
            destination = apres_connexion
        else:
            destination = url_for("public.accueil")

        reponse = redirect(destination)
        reponse.set_cookie("cookies_acceptes", "true" if accepte_cookies else "false",
                            max_age=60 * 60 * 24 * 365)
        return reponse

    return render_template("connexion.html")


@auth_bp.route("/deconnexion")
def deconnexion():
    session.clear()
    return redirect(url_for("public.accueil"))


@auth_bp.route("/api/cookies")
def api_cookies():
    """Bandeau de consentement cookies affiche en bas de page."""
    choix = request.args.get("choix")
    referer = request.headers.get("Referer") or url_for("public.accueil")
    reponse = redirect(referer)
    reponse.set_cookie("cookies_acceptes", "true" if choix == "accepter" else "false",
                        max_age=60 * 60 * 24 * 365)
    return reponse
