from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, current_app, send_file
from app.models.equipment import Equipments
from app.models.record import Records
from app.models.user import User
from app import db
from flask_login import login_required, current_user
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

bp = Blueprint('record', __name__)

@bp.before_request
@login_required
def before_request():
    pass

@bp.route('/record')
def index():
    data = Records.query.all()
    return render_template('record/index.html', data=data)

@bp.route('/record/add', methods=['GET', 'POST'])
def add():
    colombia_tz = pytz.timezone('America/Bogota')
    if request.method == 'POST':
        
        equipmentId = request.form['equipmentId']
        dataEntry = datetime.now(colombia_tz)
        dataExit = datetime.now(colombia_tz)
        apprentice_id = int(request.form.get('apprenticeId'))
        wachiman_id = int(request.form.get('wachimanId'))
        

        # userId es obligatorio, usualmente asignamos el usuario logueado
        user_id = current_user.idUser

        new_record = Records(
            userId=user_id,
            apprenticeId=apprentice_id,
            wachimanId=wachiman_id,
            dataEntry=dataEntry,
            dataExit=None,
            equipmentId=equipmentId
        )

        db.session.add(new_record)
        db.session.commit()

        return redirect(url_for('record.index'))

    equipment = Equipments.query.all()
    if current_user.rol == 'Aprendiz':
        adata = [current_user]  # Solo él mismo
    else:
        adata = User.query.filter_by(rol='Aprendiz').all()
    idata = User.query.filter_by(rol='Instructor').all()
    wdata = User.query.filter_by(rol='Celador').all()

    return render_template('record/add.html', equipments=equipment, adata=adata, idata=idata, wdata=wdata)


@bp.route('/record/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    colombia_tz = pytz.timezone('America/Bogota')
    record = Records.query.get_or_404(id)
    equipment = Equipments.query.all()
    
    
    if request.method == 'POST':
        try:
            # 🔹 Convertir la fecha de string a datetime
            
            record.dataEntry = datetime.now(colombia_tz)
            record.dataExit = datetime.strptime(request.form['dataExit'], "%Y-%m-%dT%H:%M")
            record.apprenticeId = request.form['apprenticeId']
            record.equipmentId = request.form['equipmentId']
            record.wachimanId = request.form['wachimanId']
            db.session.commit()
            return redirect(url_for('record.index'))
        
        except ValueError as e:
            flash(f"Error al actualizar préstamo: {str(e)}", "danger")
            return redirect(url_for('record.edit', id=id))
    
    adata = User.query.filter_by(rol='Aprendiz').all()
    wdata = User.query.filter_by(rol='Celador').all()
    
    return render_template('record/edit.html', record=record, equipment=equipment, adata=adata, wdata=wdata)

@bp.route('/recorsd/delete/<int:id>')
def delete(id):
    record = Records.query.get_or_404(id)
    
    db.session.delete(record)
    db.session.commit()
    
    return redirect(url_for('record.index'))

@bp.route('/salida/<int:id>', methods=['POST'])
def salida(id):
    record = Records.query.get_or_404(id)
    
    if record.dataExit:  # ya tiene salida registrada
        return jsonify({"error": "Ya tiene fecha de salida"}), 400
    
    record.dataExit = datetime.now()
    db.session.commit()
  
    return jsonify({"message": "Salida registrada correctamente"}), 200


@bp.route('/record/get_data_by_qr', methods=['GET'])
def get_data_by_qr():
    apprentice_id = request.args.get('apprenticeId')
    equipment_id = request.args.get('equipmentId')
    user_id = request.args.get('current_user.idUser')
    
    record = Records.query.filter_by(apprentice_id=apprentice_id, equipment_id=equipment_id,user_id=user_id).all()

    records_data = [{
        'idRecords': record.idRecords,
        'dataEntry': record.dataEntry,
        'dataExit':None,
        'apprenticeId': {'name': record.apprenticeId.name},
        'equipmentId': {'codeEquipment': record.equipment.codeEquipment},
        'user': {'name': record.user.name}
    } for record in records_data]
      

    return redirect('/addconqr')

@bp.route('/record/addqr/<int:id>', methods=['GET'])
@login_required
def addconqr(id):
    equipo = Equipments.query.get_or_404(id)
    colombia_tz = pytz.timezone('America/Bogota')

    apprenticeId = equipo.apprenticeId
    instructorId = equipo.instructorId

    # Ahora sí estás seguro que el usuario está logueado
    wachimanId = current_user.idUser  # o current_user.id si usas ese campo
    userId = current_user.idUser       # igual que arriba

    equipmentId = equipo.idEquipment
    dataEntry = datetime.now(colombia_tz)
    dataExit = datetime.now(colombia_tz)

    newRecord = Records(
        apprenticeId=apprenticeId,
        instructorId=instructorId,
        wachimanId=wachimanId,
        userId=userId,
        equipmentId=equipmentId,
        dataEntry=dataEntry,
        dataExit=None
    )
    db.session.add(newRecord)
    db.session.commit()

    return redirect(url_for('record.index'))

@bp.route('/generar-pdf-apr', methods=['GET', 'POST'])
def generar_pdf_apr():
    from reportlab.lib import colors
    from datetime import datetime
    from io import BytesIO

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

        registros = Records.query.filter(
            Records.dataEntry >= fecha_inicio_dt,
            Records.dataEntry <= fecha_fin_dt
        ).all()
    else:
        registros = Records.query.all()
    
    # --- Generación del PDF (igual que tu código actual) ---
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']

    # Logo y encabezado
    logo_path = os.path.join(current_app.root_path, 'static', 'img', 'logoSena.png')
    logo = Image(logo_path, 0.8 * inch, 0.8 * inch)
    header_text = Paragraph(
        "<b>CENTRO DE GESTIÓN AGROEMPRESARIAL DEL ORIENTE</b><br/>"
        "REGISTROS DE ENTRADA/SALIDA DE EQUIPOS",
        normal_style
    )
    table = Table([[logo, header_text]], colWidths=[1.0 * inch, 5.5 * inch])
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
        ('LEFTPADDING', (1, 0), (1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(table)
    story.append(Spacer(1, 20))

    # Tabla de datos
    header_style = styles['Normal']
    header_style.fontSize = 10
    header_style.alignment = 1

    data = [[
        Paragraph("FECHA<br/>ENTRADA", header_style),
        Paragraph("FECHA<br/>SALIDA", header_style),
        Paragraph("APRENDIZ", header_style),
        Paragraph("CÓDIGO<br/>EQUIPO", header_style),
        Paragraph("CELADOR", header_style)
    ]]

    for r in registros:
        data.append([
            r.dataEntry.strftime("%Y-%m-%d %H:%M") if r.dataEntry else "",
            r.dataExit.strftime("%Y-%m-%d %H:%M") if r.dataExit else "",
            r.apprentice.name if r.apprentice else "",
            r.equipment.codeEquipment if r.equipment else "",
            r.wachiman.name if r.wachiman else ""
        ])

    table = Table(data, colWidths=[110, 110, 140, 120, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2e7d32")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 1.2, colors.HexColor("#43a047")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#a5d6a7")),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))

    story.append(table)
    story.append(Spacer(1, 20))

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
