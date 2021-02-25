import os
basedir = os.path.abspath(os.path.dirname(__file__))
import secrets

class Config(object):
    # generate secret key
    # secrets.token_urlsafe(24)
    # Security TODO: 
    SECRET_KEY = 'hTIvxYgCQHCyo32QLxIZfNsKL5aI4DbJ'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevConfig(Config):
    FLASK_DEBUG = True
    FLASK_ENVIRONMENT = 'development'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'app.db')

class ProdConfig(Config):
    FLASK_DEBUG = False
    FLASK_ENVIRONMENT = 'production'
