from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sistema'  # Mover aquí antes de init_app

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(idUser):
        from .models.user import User
        return User.query.get(int(idUser))

    from app.routes import (
        login_routes,
        equipment_routes, room_routes,
        roomLoan_routes, records_routes, recordsIn_route
    )
 
 
    app.register_blueprint(login_routes.bp)
    app.register_blueprint(equipment_routes.bp)
  
    app.register_blueprint(room_routes.bp)
    app.register_blueprint(roomLoan_routes.bp)
    app.register_blueprint(records_routes.bp)
    app.register_blueprint(recordsIn_route.bp)

    return app
