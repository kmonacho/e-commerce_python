"""
Gere le paiement d'une commande EN_ATTENTE via 3 moyens :
 - CARTE   : verification Visa/Mastercard (Luhn + prefixe) + expiration + CVV
 - TWINT   : simulation via un numero de telephone (paiement mobile suisse)
 - GOOGLE_GIFT_CARD : verification du code et du solde de la carte cadeau
"""
import re
import uuid

from flask import Blueprint, abort, render_template, request, session, redirect, url_for, flash

from app.card_validator import carte_valide, cvv_valide, date_expiration_valide, determiner_type
from app.dao import carte_cadeau_dao, commande_dao, paiement_dao
from app.decorateurs import connexion_requise

paiement_bp = Blueprint("paiement", __name__)

_REGEX_TWINT = re.compile(r"^(\+41|0)7[0-9](\s?[0-9]{2,3}){3}$")


@paiement_bp.route("/paiement/<int:commande_id>", methods=["GET"])
@connexion_requise
def formulaire_paiement(commande_id):
    commande = commande_dao.trouver_par_id(commande_id)
    if not commande or commande["utilisateur_id"] != session["utilisateur_id"]:
        abort(403)
    return render_template("paiement.html", commande=commande)


@paiement_bp.route("/paiement/<int:commande_id>", methods=["POST"])
@connexion_requise
def traiter_paiement(commande_id):
    commande = commande_dao.trouver_par_id(commande_id)
    if not commande or commande["utilisateur_id"] != session["utilisateur_id"]:
        abort(403)

    mode = request.form.get("mode")  # CARTE, TWINT, GOOGLE_GIFT_CARD
    erreur = None
    reference = "ECHEC"
    succes = False

    if mode == "CARTE":
        numero_carte = request.form.get("numero_carte", "")
        mois = request.form.get("mois_expiration", "")
        annee = request.form.get("annee_expiration", "")
        cvv = request.form.get("cvv", "")

        if not carte_valide(numero_carte):
            erreur = "Numero de carte invalide : seules les cartes Visa et Mastercard sont acceptees."
        elif not date_expiration_valide(mois, annee):
            erreur = "Date d'expiration invalide ou carte expiree."
        elif not cvv_valide(cvv):
            erreur = "Code CVV invalide."

        succes = erreur is None
        if succes:
            chiffres = re.sub(r"[^0-9]", "", numero_carte)
            masque = re.sub(r"\d(?=\d{4})", "*", chiffres)
            reference = f"{determiner_type(numero_carte)} se terminant par {masque}"

    elif mode == "TWINT":
        telephone = request.form.get("telephone_twint", "")
        succes = bool(_REGEX_TWINT.match(telephone or ""))
        if not succes:
            erreur = "Numero de telephone TWINT invalide."
        else:
            reference = "TWINT-" + str(uuid.uuid4())[:8].upper()

    elif mode == "GOOGLE_GIFT_CARD":
        code_carte = request.form.get("code_carte_cadeau", "")
        succes = carte_cadeau_dao.utiliser(code_carte, float(commande["total"]))
        if not succes:
            erreur = "Code de carte cadeau invalide, deja utilise, ou solde insuffisant."
        else:
            reference = code_carte

    else:
        erreur = "Moyen de paiement inconnu."

    paiement_dao.enregistrer(commande_id, mode, reference, succes)

    if succes:
        commande_dao.marquer_payee(commande_id, mode)
        flash("Paiement accepte, votre commande est validee !", "succes")
        return redirect(url_for("commande.mes_commandes"))

    return render_template("paiement.html", commande=commande, erreur=erreur)
