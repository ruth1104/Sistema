from flask import Blueprint, render_template, request, redirect, url_for, send_file
from app.models.equipment import Equipments
from io import BytesIO
import base64
from flask_login import login_required, current_user
from app import db
from app.models.user import User


bp = Blueprint('equipment', __name__)

@bp.before_request
@login_required
def before_request():
    pass

@bp.route('/equipment/index')
def index():
    
    if current_user.rol == 'Instructor':
        data = current_user.equipmenti
    elif current_user.rol == 'Aprendiz':
        data = current_user.equipmenta
    elif current_user.rol == 'Celador':
        data = Equipments.query.all()
   
    return render_template('equipment/index.html', data=data)

@bp.route('/equipment/index1')
def index1():
    data = current_user.equipment

    return render_template('equipment/index.html', data=data)


@bp.route('/equipment/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        brandEquipment = request.form['brandEquipment']
        codeEquipment = request.form['codeEquipment']
        accassoriesEquipment = request.form['accassoriesEquipment']
        
        # Aquí tomamos los IDs seleccionados en el formulario
        apprenticeId = request.form.get('apprenticeId')  
        instructorId = request.form.get('instructorId')  #

        newEquipment = Equipments(
            brandEquipment=brandEquipment,
            codeEquipment=codeEquipment,
            accassoriesEquipment=accassoriesEquipment,
            apprenticeId=apprenticeId if apprenticeId else None,
            instructorId=instructorId if instructorId else None
        )

        db.session.add(newEquipment)
        db.session.commit()
        
        return redirect(url_for('equipment.index'))

    # Para el GET, obtenemos listas para los selects en el formulario
    adata = User.query.filter_by(rol='Aprendiz').all()
    idata = User.query.filter_by(rol='Instructor').all()
    return render_template('equipment/add.html', adata=adata, idata=idata)


@bp.route('/equipment/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    equipment= Equipments.query.get_or_404(id)
    instructorId = User.query.all()
    apprenticeId = User.query.all()

    if request.method == 'POST':
        equipment.brandEquipment = request.form['brandEquipment']
        equipment.codeEquipment =request.form['codeEquipment']
        equipment.accassoriesEquipment= request.form ['accassoriesEquipment']
        equipment.apprenticeId= request.form ['apprenticeId']
        equipment.instructorId= request.form ['instructorId']
        db.session.commit()        
        return redirect(url_for('equipment.index'))

    return render_template('equipment/edit.html', equipment=equipment, apprenticeId = apprenticeId, instructorId=instructorId)

@bp.route('/equipment/delete/<int:id>')
def delete(id):
   equipment = Equipments.query.get_or_404(id)
   db.session.delete(equipment)
   db.session.commit()
   
   return redirect(url_for('equipment.index'))

@bp.route('/qr/<int:id>')
def generate_qr(id):
    
    equipement = Equipments.query.get_or_404(id)
    qr_code_base64 = equipement.generate_qr()
    # Decodificar la imagen del QR desde base64
    qr_code_img = base64.b64decode(qr_code_base64)
    return send_file(BytesIO(qr_code_img), mimetype='image/png')


