from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import login_user, logout_user, login_required
from app import db
from app.models.user import User
from app.models.record import Records
from flask_login import current_user

bp = Blueprint('auth', __name__)


@bp.route('/indexUser')
@login_required
def indexuser():
    users = User.query.all()

    # Aplica filtros según el rol
    if current_user.rol == 'Instructor':
        users = [u for u in users if u.idUser == current_user.idUser]
    elif current_user.rol == 'Aprendiz':
        users = [u for u in users if u.idUser == current_user.idUser]
    data = Records.query.all()
    return render_template('login/index.html', users=users,data=data)


@bp.route('/inderecord')
@login_required
def index():
    users = User.query.all()

    # Aplica filtros según el rol
    if current_user.rol == 'Instructor':
        users = [u for u in users if u.idUser == current_user.idUser]
    if current_user.rol == 'Aprendiz':
        users = [u for u in users if u.idUser == current_user.idUser]
    if current_user.rol in ['Instructor', 'Aprendiz']:
        return redirect(url_for('auth.indexuser'))
        
    data = Records.query.all()
    return render_template('record/index.html', users=users,data=data)

@bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        documento = request.form.get("documento")
        password = request.form.get("passwordUser")

        print("Documento recibido:", documento)
        print("Password recibido:", password)

        user = User.query.filter_by(documento=documento).first()

        print("Resultado de la consulta user:", user)

        if user:
            print("Contraseña en base de datos:", user.password)
            if user.password == password:
                login_user(user)
                
                
                session['usuario_id'] = user.idUser
                session['usuario_nombre'] = user.name
                session['usuario_rol'] = user.rol
                return redirect(url_for("auth.index"))
            else:
                flash("Contraseña incorrecta", "danger")
        else:
            flash("Usuario no encontrado", "danger")

    return render_template("login/login.html")




@bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear() 
    return redirect(url_for('auth.login'))

@bp.route('/add', methods=['GET', 'POST'])    
def add():
    if request.method == 'POST':
        documento = request.form.get('documento')
        name = request.form.get('name')       
        password = request.form.get('password')
        Tel = request.form.get('Tel')         
        gmail = request.form.get('gmail')     
        rol = request.form.get('rol', 'Aprendiz')  

       
        existing_user = User.query.filter_by(documento=documento).first()
        if existing_user:
            flash('El nombre de usuario ya está registrado', 'error')
            return redirect(url_for('auth.add'))

        
        new_user = User(documento=documento, name=name, password=password, Tel=Tel, gmail=gmail, rol=rol)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("auth.index"))

    adata = User.query.filter_by(rol='Aprendiz').all()
    idata = User.query.filter_by(rol='Instructor').all()
    return render_template('login/add.html', adata=adata, idata=idata)

@bp.route('/user/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    user = User.query.get_or_404(id)

    if request.method == 'POST':
        user.documento = request.form['documento']
        new_password = request.form['password']
        if new_password:
            user.password = new_password
        user.rol = request.form['rol']
        db.session.commit()
            
        if current_user.idUser == 1 and 'rolUser' in request.form:
            user.rolUser = request.form['rolUser']
            
        return redirect(url_for('auth.index'))

    return render_template('login/edit.html', user=user)

@bp.route('/user/delete/<int:id>')
def delete(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('auth.index'))