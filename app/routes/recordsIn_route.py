from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, send_file, current_app
from app.models.equipment import Equipments
from app.models.recordsIn import RecordsIn
from app.models.user import User
from flask_login import login_required,current_user
from app import db
from datetime import datetime
import pytz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import inch
from io import BytesIO
import os



bp = Blueprint('recordsIn', __name__)

@bp.before_request
@login_required
def before_request():
    pass

@bp.route('/recordsIn')
def index():
    data = RecordsIn.query.all()
    return render_template('recordsIn/index.html', data=data)

@bp.route('/recordsIn/add', methods=['GET', 'POST'])
def add():
    colombia_tz = pytz.timezone('America/Bogota')
    if request.method == 'POST':
        equipmentId = request.form['equipmentId']
        dataEntry = datetime.now(colombia_tz)
        dataExit = datetime.now(colombia_tz)
        instructorId = request.form.get('instructorId')
        wachimanId = request.form.get('wachimanId')
        
        
        # userId es obligatorio, usualmente asignamos el usuario logueado
        user_id = current_user.idUser
        
        newRecordsIn = RecordsIn(
            userId=user_id,
            instructorId=instructorId,
            wachimanId=wachimanId, 
            dataEntry=dataEntry, 
            dataExit=None,
            equipmentId=equipmentId)
        
        db.session.add(newRecordsIn)
        db.session.commit()
        
        return redirect(url_for('recordsIn.index'))
    
    equipment = Equipments.query.all()
    adata = User.query.filter_by(rol='Aprendiz').all()
    if current_user.rol == 'Instructor':
        idata = [current_user]  # Solo él mismo
    else:
        idata = User.query.filter_by(rol='Instructor').all()
    wdata = User.query.filter_by(rol='Celador').all()
    
    return render_template('recordsIn/add.html', equipments=equipment, adata=adata, idata=idata, wdata=wdata)

@bp.route('/recordIn/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    colombia_tz = pytz.timezone('America/Bogota')
    recordsIn = RecordsIn.query.get_or_404(id)
    equipment = Equipments.query.all()
   
    if request.method == 'POST':
        try:
            # 🔹 Convertir la fecha de string a datetime
            
            recordsIn.dataEntry = datetime.now(colombia_tz)
            recordsIn.dataExit = datetime.strptime(request.form['dataExit'], "%Y-%m-%dT%H:%M")
            recordsIn.instructorId = request.form['instructorId']
            recordsIn.equipmentId = request.form['equipmentId']
            recordsIn.wachimanId = request.form['wachimanId']
            db.session.commit()
            return redirect(url_for('recordsIn.index'))
        
        except ValueError as e:
            flash(f"Error al actualizar préstamo: {str(e)}", "danger")
            return redirect(url_for('recordsIn.edit', id=id))
    
    idata = User.query.filter_by(rol='Instructor').all()
    wdata = User.query.filter_by(rol='Celador').all()
    return render_template('recordsIn/edit.html', recordsIn=recordsIn, equipment=equipment, idata=idata, wdata=wdata)

@bp.route('/delete/registro_instructor/<int:id>')
def delete(id):
    recordsIn = RecordsIn.query.get_or_404(id)
    
    db.session.delete(recordsIn)
    db.session.commit()
    
    return redirect(url_for('recordsIn.index'))

@bp.route('/salida/registro_instructor/<int:id>', methods=['POST'])
def salida(id):
    recordsIn = RecordsIn.query.get_or_404(id)
    
    if RecordsIn.dataExit:  # ya tiene salida registrada
        return jsonify({"error": "Ya tiene fecha de salida"}), 400
    
    recordsIn.dataExit = datetime.now()
    db.session.commit()
  
    return jsonify({"message": "Salida registrada correctamente"}), 200

@bp.route('/recordsIn/get_data_by_qr', methods=['GET'])
def get_data_by_qr():
    instructor_id = request.args.get('equipmentId')
    equipment_id = request.args.get('equipmentId')
    user_id = request.args.get('current_user.idUser')
    
    recordIns = RecordsIn.query.filter_by(instructor_id=instructor_id, equipment_id=equipment_id, user_id=user_id).all()

    records_data = [{
        'idRecords': recordIns.idRecords,
        'dataEntry': recordIns.dataEntry,
        'dataExit': None,
        'instructor': {'nameInstructor': recordIns.instructor.nameInstructor},
        'user': {'documento': recordIns.user.documento},
        'equipment': {'codeEquipment': recordIns.equipment.codeEquipment},
        
    } for recordIns in records_data]
      

    return redirect('/addconqr')

@bp.route('/recordsIn/addqr/<int:id>', methods=['GET'])
@login_required
def addconqr(id):
    equipo = Equipments.query.get_or_404(id)
    colombia_tz = pytz.timezone('America/Bogota')


    instructorId = equipo.instructorId

    # Ahora sí estás seguro que el usuario está logueado
    wachimanId = current_user.idUser  # o current_user.id si usas ese campo
    userId = current_user.idUser       # igual que arriba

    equipmentId = equipo.idEquipment
    dataEntry = datetime.now(colombia_tz)
    dataExit = datetime.now(colombia_tz)

    newRecord = RecordsIn(
      
        instructorId=instructorId,
        wachimanId=wachimanId,
        userId=userId,
        equipmentId=equipmentId,
        dataEntry=dataEntry,
        dataExit=None
    )
    db.session.add(newRecord)
    db.session.commit()

    return redirect(url_for('recordsIn.index'))
@bp.route('/generar-pdf-Ins')
def generar_pdf_Ins():
    from reportlab.lib import colors
    
    if request.method == 'POST':
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')

        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%dT%H:%M')
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%dT%H:%M')
            print(fecha_inicio_dt)
            print(fecha_fin_dt)

        except ValueError:
            flash("Formato de fecha inválido", "danger")
            return redirect(url_for('auth.index'))  # cambia si es otra ruta

        registros = RecordsIn.query.filter(
            RecordsIn.dataEntry >= fecha_inicio_dt,
            RecordsIn.dataEntry <= fecha_fin_dt
        ).all()
    else:
        registros = RecordsIn.query.all()
        
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']

    # Cargar el logo
    logo_path = os.path.join(current_app.root_path, 'static', 'img', 'logoSena.png')
    logo = Image(logo_path, 0.8 * inch, 0.8 * inch)

    # Crear el texto del encabezado (título + subtítulo en un solo Paragraph)
    header_text = Paragraph(
        "<b>CENTRO DE GESTIÓN AGROEMPRESARIAL DEL ORIENTE</b><br/>"
        "REGISTROS DE ENTRADA/SALIDA DE EQUIPOS",
        normal_style
    )

    # Crear la tabla con logo y texto
    table_data = [[logo, header_text]]
    table = Table(table_data, colWidths=[1.5 * inch, 5.5 * inch])

    # Estilo de la tabla
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
        ('LEFTPADDING', (1, 0), (1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
    ]))

    story.append(table)
    story.append(Spacer(1, 20))

    data = [['FECHA DE ENTRADA', 'FECHA DE SALIDA', 'INSTRUCTOR', 'CÓDIGO DE EQUIPO', 'CELADOR']]

    registros = RecordsIn.query.all()
    for r in registros:
        data.append([
            r.dataEntry.strftime("%Y-%m-%d %H:%M") if r.dataEntry else "",
            r.dataExit.strftime("%Y-%m-%d %H:%M") if r.dataExit else "",
            r.instructor.nameInstructor if r.instructor else "",
            
            r.equipment.codeEquipment if r.equipment else "",
            r.user.documento if r.user else ""
        ])

    from reportlab.lib import colors

    table = Table(data, colWidths=[110, 110, 140, 120, 100])
    table.setStyle(TableStyle([
         # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2e7d32")),  # Verde oscuro
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 8),

        # Contenido
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),

        # Bordes y rejilla
        ('BOX', (0, 0), (-1, -1), 1.2, colors.HexColor("#43a047")),  # Borde verde medio
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#a5d6a7")),

        # Padding
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))

    story.append(table)
    story.append(Spacer(1, 20))

    # Pie de página
    footer = Paragraph(
        "Este documento fue generado automáticamente por el sistema de control de equipos 2025.",
        normal_style
    )
    story.append(footer)
    story.append(Spacer(1, 24))
    
    doc.build(story)
    buffer.seek(0)
    filename = f"registro_Aprendices_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.pdf"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')
