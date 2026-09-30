from flask import Blueprint, flash, redirect, render_template, session, url_for

from app.dao import commande_dao
from app.decorateurs import connexion_requise

commande_bp = Blueprint("commande", __name__)


@commande_bp.route("/commande")
@connexion_requise
def mes_commandes():
    commandes = commande_dao.lister_par_utilisateur(session["utilisateur_id"])
    return render_template("commandes.html", commandes=commandes)


@commande_bp.route("/commande/creer", methods=["POST"])
@connexion_requise
def creer_commande():
    utilisateur_id = session["utilisateur_id"]
    commande_id = commande_dao.passer_commande(utilisateur_id)
    if commande_id is None:
        flash("Votre panier est vide ou le stock est insuffisant.", "erreur")
        return redirect(url_for("panier.voir_panier"))
    return redirect(url_for("paiement.formulaire_paiement", commande_id=commande_id))


@commande_bp.route("/commande/annuler/<int:commande_id>")
@connexion_requise
def annuler_commande(commande_id):
    ok = commande_dao.annuler_commande(commande_id, session["utilisateur_id"])
    flash("Commande annulee, le stock a ete restitue." if ok else "Impossible d'annuler cette commande.",
          "succes" if ok else "erreur")
    return redirect(url_for("commande.mes_commandes"))
