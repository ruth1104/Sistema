from app import db

class RecordsIn(db.Model):
    __tablename__ = 'recordsIn'
    idRecordsIn = db.Column(db.Integer, primary_key=True)
    dataEntry = db.Column(db.DateTime, nullable=False)
    dataExit = db.Column(db.DateTime, nullable=True)
    
    wachimanId = db.Column(db.Integer, db.ForeignKey('user.idUser'))
    equipmentId = db.Column(db.Integer, db.ForeignKey('equipment.idEquipment'))
    userId = db.Column(db.Integer, db.ForeignKey('user.idUser'))
    instructorId = db.Column(db.Integer, db.ForeignKey('user.idUser'))

    # Relaciones por rol
    user = db.relationship('User', back_populates='recordsIn', foreign_keys=[userId])           # Usuario normal
    wachiman = db.relationship('User', back_populates='recordsInW', foreign_keys=[wachimanId]) 
    instructor = db.relationship("User", foreign_keys=[instructorId], back_populates="recordsInI")# Wachimán
    equipment = db.relationship("Equipments", back_populates="recordsIn")                       # Equipo
