from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.dao import panier_dao, taille_dao
from app.decorateurs import connexion_requise

panier_bp = Blueprint("panier", __name__)


@panier_bp.route("/panier")
@connexion_requise
def voir_panier():
    utilisateur_id = session["utilisateur_id"]
    items = panier_dao.lister_par_utilisateur(utilisateur_id)
    total = sum(item["sous_total"] for item in items)
    return render_template("panier.html", items=items, total=total)


@panier_bp.route("/panier/ajouter", methods=["POST"])
@connexion_requise
def ajouter_au_panier():
    utilisateur_id = session["utilisateur_id"]
    try:
        taille_id = int(request.form["taille_id"])
        quantite = max(1, int(request.form.get("quantite", 1)))
    except (KeyError, ValueError):
        flash("Requete invalide.", "erreur")
        return redirect(url_for("public.accueil"))

    taille = taille_dao.trouver_par_id(taille_id)
    if not taille or taille["stock"] < quantite:
        flash("Stock insuffisant pour cette taille.", "erreur")
    else:
        panier_dao.ajouter_ou_incrementer(utilisateur_id, taille_id, quantite)
        flash("Article ajoute au panier.", "succes")

    return redirect(request.referrer or url_for("public.accueil"))


@panier_bp.route("/panier/supprimer", methods=["POST"])
@connexion_requise
def supprimer_du_panier():
    utilisateur_id = session["utilisateur_id"]
    item_id = int(request.form["item_id"])
    panier_dao.supprimer_item(item_id, utilisateur_id)
    return redirect(url_for("panier.voir_panier"))
