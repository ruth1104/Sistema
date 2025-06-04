from app import db
from datetime import datetime

class RoomsLoans(db.Model):
    __tablename__ = 'roomLoan'
    
    idRoomLoan = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    returnDate = db.Column(db.DateTime, nullable=True)

    wachimanId = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=True)
    instructorId = db.Column(db.Integer, db.ForeignKey('user.idUser'))
    userId = db.Column(db.Integer, db.ForeignKey('user.idUser'))
    roomId = db.Column(db.Integer, db.ForeignKey('room.idRoom'))
    
    # Relaciones por roles
    user = db.relationship('User', back_populates='roomLoan', foreign_keys=[userId])            # Usuario solicitante
    wachiman = db.relationship('User', back_populates='roomLoan', foreign_keys=[wachimanId])    # Celador
    instructor = db.relationship('User', back_populates='roomLoan', foreign_keys=[instructorId])# Instructor responsable
    room = db.relationship('Rooms', back_populates='roomLoan', foreign_keys=[roomId])            # Sala prestada
