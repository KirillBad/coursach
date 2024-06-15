from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from . import config

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["UPLOAD_FOLDER"] = "website/static"
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}/{config.DB_NAME}"
    )
    db.init_app(app)
    migrate.init_app(app, db)

    from .home import home_bp
    from .auth import auth_bp
    from .payments import payments_bp

    app.register_blueprint(home_bp, url_prefix="/")
    app.register_blueprint(auth_bp, url_prefix="/")
    app.register_blueprint(payments_bp, url_prefix="/")

    from .models import User

    create_db(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_db(app):
    with app.app_context():
        db.create_all()
