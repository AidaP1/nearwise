import os

class DefaultConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    DATABASE_URL = os.getenv('PROD_DATABASE_URL', 'sqlite:///myapp.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProdConfig(DefaultConfig):
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    DATABASE_URL = os.getenv('PROD_DATABASE_URL', 'sqlite:///myapp.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    pass

class StagingConfig(DefaultConfig):
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    DATABASE_URL = os.getenv('STAGING_DATABASE_URL', 'sqlite:///myapp.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    pass