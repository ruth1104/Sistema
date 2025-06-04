# config.py
import secrets

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///flaskdb.sqlite'
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@localhost:3306/sistema'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = secrets.token_urlsafe(24)