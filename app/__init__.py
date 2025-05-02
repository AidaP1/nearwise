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

def create_app():
    load_dotenv()
    app = Flask(__name__)

   # Determine config object: use argument, then APP_CONFIG env var, then default
    config_object = config_object or os.getenv("APP_CONFIG", "config.DefaultConfig")
    app.config.from_object(config_object)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')

    if os.getenv('RENDER') == 'true':
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    else:
        basedir = os.path.abspath(os.path.dirname(__file__))
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '..', 'myapp.db')
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
