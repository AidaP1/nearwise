import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv
from .logger import setup_logger

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
logger = setup_logger(__name__)

def create_app(config_object=None):
    load_dotenv()
    app = Flask(__name__)

   # Determine config object: use argument, then APP_CONFIG env var, then default
    if not config_object:
        if os.environ.get("RENDER") == "true":
            config_object = os.getenv("APP_CONFIG", "app.config.DefaultConfig")
        else: config_object = "app.config.LocalConfig"
    app.config.from_object(config_object)

    print(f"Loaded config: {app.config['SQLALCHEMY_DATABASE_URI']}")

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_view = 'main.login'

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from .routes.main import main_bp
    app.register_blueprint(main_bp)

    # Error handling
    @app.errorhandler(404)
    def not_found(e):
        logger.warning(f"404: {e}")
        return "Page not found", 404

    @app.errorhandler(500)
    def internal_error(e):
        logger.exception("500 error")
        db.session.rollback()
        return "Internal server error", 500

    return app
