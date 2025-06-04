import os
import secrets
from dotenv import load_dotenv
load_dotenv()

class Config:
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_HOST = os.environ.get("DB_HOST")
    raw_port = os.environ.get("DB_PORT")
    if not raw_port or raw_port == "{DB_PORT}":
        DB_PORT = "3311"
    else:
        DB_PORT = raw_port
    DB_NAME = os.environ.get("DB_NAME")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = secrets.token_urlsafe(24)

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"