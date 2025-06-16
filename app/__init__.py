from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
import os

from app.models import db, User

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

csrf = CSRFProtect()


def create_app():
    app = Flask(__name__, static_folder='../static')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'devsecret')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///equipment.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/uploads/'
    app.config['DISPOSAL_FOLDER'] = os.path.join(app.root_path, 'static', 'disposals')
    
    db.init_app(app)
    Migrate(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)

    from app.routes import equipment, auth, disposal, maintenance
    app.register_blueprint(equipment.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(disposal.bp)
    app.register_blueprint(maintenance.bp)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app