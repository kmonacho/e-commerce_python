from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.dao import (
    chaussure_dao,
    collection_dao,
    commande_dao,
    marque_dao,
    message_dao,
    partenaire_dao,
    taille_dao,
)
from app.decorateurs import admin_requis

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/tableau-de-bord")
@admin_requis
def tableau_de_bord():
    return render_template(
        "admin/tableau_de_bord.html",
        nb_chaussures=len(chaussure_dao.lister_toutes()),
        nb_commandes=len(commande_dao.lister_toutes()),
        nb_partenaires=len(partenaire_dao.lister_tous()),
        nb_messages=len(message_dao.lister_tous()),
    )


# ---------------------------------------------------------------- Chaussures
@admin_bp.route("/chaussures")
@admin_requis
def liste_chaussures():
    chaussures = chaussure_dao.lister_toutes()
    return render_template("admin/chaussures.html", chaussures=chaussures)


@admin_bp.route("/chaussures/nouveau", methods=["GET", "POST"])
@admin_requis
def nouvelle_chaussure():
    if request.method == "POST":
        _enregistrer_chaussure()
        return redirect(url_for("admin.liste_chaussures"))

    return render_template(
        "admin/chaussure_formulaire.html",
        marques=marque_dao.lister_toutes(),
        collections=collection_dao.lister_toutes(),
        genres=["HOMME", "FEMME", "UNISEXE"],
        chaussure=None,
    )


@admin_bp.route("/chaussures/<int:chaussure_id>/modifier", methods=["GET", "POST"])
@admin_requis
def modifier_chaussure(chaussure_id):
    if request.method == "POST":
        _enregistrer_chaussure(chaussure_id)
        return redirect(url_for("admin.liste_chaussures"))

    chaussure = chaussure_dao.trouver_par_id(chaussure_id)
    return render_template(
        "admin/chaussure_formulaire.html",
        marques=marque_dao.lister_toutes(),
        collections=collection_dao.lister_toutes(),
        genres=["HOMME", "FEMME", "UNISEXE"],
        chaussure=chaussure,
    )


def _enregistrer_chaussure(chaussure_id=None):
    date_sortie = request.form.get("date_sortie") or None
    donnees = {
        "modele": request.form["modele"],
        "marque_id": int(request.form["marque_id"]),
        "date_sortie": date_sortie,
        "prix": float(request.form["prix"]),
        "genre": request.form["genre"],
        "collection_id": int(request.form.get("collection_id") or 1),
        "description": request.form.get("description", ""),
        "image_url": request.form.get("image_url", ""),
    }
    if chaussure_id:
        chaussure_dao.modifier(chaussure_id, donnees)
    else:
        chaussure_dao.creer(donnees)


@admin_bp.route("/chaussures/<int:chaussure_id>/supprimer")
@admin_requis
def supprimer_chaussure(chaussure_id):
    chaussure_dao.supprimer(chaussure_id)
    return redirect(url_for("admin.liste_chaussures"))


# --------------------------------------------------------------------- Tailles
@admin_bp.route("/chaussures/<int:chaussure_id>/tailles")
@admin_requis
def gerer_tailles(chaussure_id):
    chaussure = chaussure_dao.trouver_par_id(chaussure_id)
    return render_template("admin/tailles.html", chaussure=chaussure)


@admin_bp.route("/chaussures/<int:chaussure_id>/tailles/ajouter", methods=["POST"])
@admin_requis
def ajouter_taille(chaussure_id):
    taille_dao.ajouter(
        chaussure_id,
        float(request.form["taille_us"]),
        float(request.form["taille_fr"]),
        int(request.form["stock"]),
    )
    return redirect(url_for("admin.gerer_tailles", chaussure_id=chaussure_id))


@admin_bp.route("/tailles/<int:taille_id>/stock", methods=["POST"])
@admin_requis
def modifier_stock_taille(taille_id):
    chaussure_id = int(request.form["chaussure_id"])
    taille_dao.modifier_stock(taille_id, int(request.form["stock"]))
    return redirect(url_for("admin.gerer_tailles", chaussure_id=chaussure_id))


@admin_bp.route("/tailles/<int:taille_id>/supprimer", methods=["POST"])
@admin_requis
def supprimer_taille(taille_id):
    chaussure_id = int(request.form["chaussure_id"])
    taille_dao.supprimer(taille_id)
    return redirect(url_for("admin.gerer_tailles", chaussure_id=chaussure_id))


# ----------------------------------------------------------------- Collections
@admin_bp.route("/collections", methods=["GET", "POST"])
@admin_requis
def gerer_collections():
    """Permet a l'administrateur de reajouter/creer de nouvelles collections."""
    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        if nom:
            collection_dao.creer(nom)
            flash(f"Collection '{nom}' ajoutee.", "succes")
        else:
            flash("Le nom de la collection ne peut pas etre vide.", "erreur")
        return redirect(url_for("admin.gerer_collections"))

    return render_template("admin/collections.html", collections=collection_dao.lister_toutes())


# ----------------------------------------------------------------- Partenaires
@admin_bp.route("/partenaires", methods=["GET", "POST"])
@admin_requis
def gerer_partenaires():
    if request.method == "POST":
        partenaire_dao.creer(
            request.form["nom"],
            request.form.get("description", ""),
            request.form.get("logo_url", ""),
            request.form.get("site_web", ""),
        )
        return redirect(url_for("admin.gerer_partenaires"))

    return render_template("admin/partenaires.html", partenaires=partenaire_dao.lister_tous())


@admin_bp.route("/partenaires/<int:partenaire_id>/supprimer")
@admin_requis
def supprimer_partenaire(partenaire_id):
    partenaire_dao.supprimer(partenaire_id)
    return redirect(url_for("admin.gerer_partenaires"))


# ------------------------------------------------------------------ Commandes
@admin_bp.route("/commandes")
@admin_requis
def gerer_commandes():
    return render_template("admin/commandes.html", commandes=commande_dao.lister_toutes())


# -------------------------------------------------------------------- Messages
@admin_bp.route("/messages")
@admin_requis
def gerer_messages():
    return render_template("admin/messages.html", messages=message_dao.lister_tous())


@admin_bp.route("/messages/<int:message_id>/marquer-lu")
@admin_requis
def marquer_message_lu(message_id):
    message_dao.marquer_lu(message_id)
    return redirect(url_for("admin.gerer_messages"))
