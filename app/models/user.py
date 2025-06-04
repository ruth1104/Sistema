from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    idUser = db.Column(db.Integer, primary_key=True)
    documento = db.Column(db.String(300), unique=True, nullable=False)
    name = db.Column(db.String(300), nullable=False)
    password = db.Column(db.String(300), nullable=False)
    Tel = db.Column(db.String(300), nullable=False)
    gmail = db.Column(db.String(300), nullable=False)
    rol = db.Column(db.String(300), nullable=True, default="Aprendiz") 
    
    
    roomLoan = db.relationship("RoomsLoans", back_populates="user",foreign_keys="RoomsLoans.userId")
    record = db.relationship("Records", back_populates="user", foreign_keys="Records.userId")
    recordsIn = db.relationship("RecordsIn", back_populates="user", foreign_keys="RecordsIn.userId")
     #equipment = db.relationship("Equipments", back_populates="user")
    
    # Relaciones por rol
    recordsw = db.relationship("Records", back_populates="wachiman", foreign_keys="Records.wachimanId")  # Celador
    recordsa = db.relationship("Records", back_populates="apprentice", foreign_keys="Records.apprenticeId")  # Aprendiz
    recordsi = db.relationship("Records", back_populates="instructor", foreign_keys="Records.instructorId")  # Instructor
    
    equipmentu = db.relationship("Equipments", back_populates="user", foreign_keys="[Equipments.userId]")
    equipmenta = db.relationship("Equipments", back_populates="apprentice", foreign_keys="[Equipments.apprenticeId]")
    equipmenti = db.relationship("Equipments", back_populates="instructor", foreign_keys="[Equipments.instructorId]")

    # Relaciones con registros de entrada (RecordsIn)
    recordsIn = db.relationship("RecordsIn", back_populates="user", foreign_keys="RecordsIn.userId")         # Usuario normal
    recordsInW = db.relationship("RecordsIn", back_populates="wachiman", foreign_keys="RecordsIn.wachimanId") 
    recordsInI = db.relationship("RecordsIn", back_populates="instructor", foreign_keys="RecordsIn.instructorId")# Wachimán

    def get_id(self):
        return str(self.idUser)