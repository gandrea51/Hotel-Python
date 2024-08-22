from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

def register_error_handlers(app):

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', error_code=404, error_massage='La pagina che stai cercando non esiste'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html', error_code=500, error_message="Errore interno del server. Per favore riprova più tardi."), 500

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('error.html', error_code=403, error_message="Accesso negato. Non hai i permessi necessari per accedere a questa pagina."), 403

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return db.session.get(User, int(user_id))
