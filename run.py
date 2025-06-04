from app import create_app,db
from app.models.user import User
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask import session

import os

app = create_app()

with app.app_context():
    db.create_all()
    
@app.context_processor
def inject_user():
    return dict(
        usuario_nombre=session.get('usuario_nombre'),
        usuario_rol=session.get('usuario_rol')
    )


if __name__ == '__main__':
     app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8084)))