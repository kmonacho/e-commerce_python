from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.dao import chaussure_dao, message_dao, partenaire_dao

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def racine():
    return redirect(url_for("public.accueil"))


@public_bp.route("/accueil")
def accueil():
    chaussures = chaussure_dao.lister_toutes()
    return render_template("accueil.html", chaussures=chaussures)


@public_bp.route("/femmes")
def femmes():
    chaussures = chaussure_dao.lister_par_genre("FEMME")
    return render_template("categorie.html", chaussures=chaussures, genre="FEMME",
                            titre="Chaussures femmes")


@public_bp.route("/hommes")
def hommes():
    chaussures = chaussure_dao.lister_par_genre("HOMME")
    return render_template("categorie.html", chaussures=chaussures, genre="HOMME",
                            titre="Chaussures hommes")


@public_bp.route("/chaussure/<int:chaussure_id>")
def detail_chaussure(chaussure_id):
    chaussure = chaussure_dao.trouver_par_id(chaussure_id)
    if not chaussure:
        abort(404)
    return render_template("detail.html", chaussure=chaussure)


@public_bp.route("/partenaires")
def partenaires():
    liste = partenaire_dao.lister_tous()
    return render_template("partenaires.html", partenaires=liste)


@public_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        email = request.form.get("email", "").strip()
        sujet = request.form.get("sujet", "").strip()
        message = request.form.get("message", "").strip()

        erreur = None
        if not nom or not email or "@" not in email or not message:
            erreur = "Merci de renseigner un nom, un email valide et un message."

        if erreur:
            return render_template("contact.html", erreur=erreur, nom=nom, email=email,
                                    sujet=sujet, message=message)

        message_dao.creer(nom, email, sujet, message)
        flash("Votre message a bien ete envoye, merci !", "succes")
        return redirect(url_for("public.contact"))

    return render_template("contact.html")
