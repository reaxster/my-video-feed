import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or b'\x95R\xe3\x10w\xacT\x15\x07\xc1\x18\x96\xe9mUq'

class BaseConfig(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False  

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'

class ProductionConfig(BaseConfig):
    DEBUG = True
    TESTING = True

config = {
    "default": "main.config.BaseConfig",
    "development": "main.config.DevelopmentConfig",
    "production": "main.config.ProductionConfig",
}

def configure_app(app):
    config_name= os.getenv('FLASK_ENV')
    app.config.from_object(config[config_name])
    app.config.from_pyfile('application.cfg', silent=True)
