from flask import Blueprint, render_template, request, redirect, url_for, send_file
from app.models.room import Rooms
from app.models.user import User
from flask_login import login_required, current_user
from io import BytesIO
from pyzbar.pyzbar import decode
import base64
from app import db

bp = Blueprint('room', __name__)

@bp.before_request
@login_required
def before_request():
    pass

@bp.route('/room')
def index():
    data = Rooms.query.all()   
    return render_template('room/index.html', data=data)

@bp.route('/room/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        nameRoom = request.form['nameRoom']
        
        newRoom = Rooms(nameRoom=nameRoom)
        db.session.add(newRoom)
        db.session.commit()
        
        return redirect(url_for('room.index'))

    return render_template('room/add.html')

@bp.route('/room/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    room= Rooms.query.get_or_404(id)

    if request.method == 'POST':
        room.nameRoom = request.form['nameRoom']
        db.session.commit()        
        return redirect(url_for('room.index'))

    return render_template('room/edit.html', room=room)

@bp.route('/room/delete/<int:id>')
def delete(id):
   room = Rooms.query.get_or_404(id)
   
   db.session.delete(room)
   db.session.commit()
   
   return redirect(url_for('room.index'))

@bp.route('/qrroom/<int:id>')
def generate_qr(id):
    print("Entrando a la ruta de generación de QR:", id)
    room = Rooms.query.get_or_404(id)
    qr_code_base64 = room.generate_qr()
    # Decodificar la imagen del QR desde base64
    qr_code_img = base64.b64decode(qr_code_base64)
    return send_file(BytesIO(qr_code_img), mimetype='image/png')
