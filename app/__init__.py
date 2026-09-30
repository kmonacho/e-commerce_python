from flask import Flask

from config import Config


def creer_application():
    """Fabrique de l'application Flask (application factory pattern)."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Connexion / deconnexion propre de la base de donnees a chaque requete
    from app.db import fermer_connexion_bd
    app.teardown_appcontext(fermer_connexion_bd)

    # Enregistrement des blueprints (routes)
    from app.routes.public import public_bp
    from app.routes.auth import auth_bp
    from app.routes.panier import panier_bp
    from app.routes.commande import commande_bp
    from app.routes.paiement import paiement_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(panier_bp)
    app.register_blueprint(commande_bp)
    app.register_blueprint(paiement_bp)
    app.register_blueprint(admin_bp)

    # Pages d'erreur
    from flask import render_template

    @app.errorhandler(404)
    def page_non_trouvee(e):
        return render_template("erreur_404.html"), 404

    @app.errorhandler(403)
    def acces_refuse(e):
        return render_template("erreur_403.html"), 403

    @app.errorhandler(500)
    def erreur_serveur(e):
        return render_template("erreur_500.html"), 500

    return app
