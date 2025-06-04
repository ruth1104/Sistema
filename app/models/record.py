from app import db

class Records(db.Model):
    __tablename__ = 'record'
    idRecords = db.Column(db.Integer, primary_key=True)
    dataEntry = db.Column(db.DateTime, nullable=False)
    dataExit = db.Column(db.DateTime, nullable=True)
    
    userId = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=False)  
    apprenticeId = db.Column(db.Integer, db.ForeignKey('user.idUser'))
    instructorId = db.Column(db.Integer, db.ForeignKey('user.idUser'))
    wachimanId = db.Column(db.Integer, db.ForeignKey('user.idUser'))
    equipmentId = db.Column(db.Integer, db.ForeignKey('equipment.idEquipment'))

    # Relaciones personalizadas
    user = db.relationship("User", foreign_keys=[userId], back_populates="record")
    apprentice = db.relationship("User", foreign_keys=[apprenticeId], back_populates="recordsa")
    instructor = db.relationship("User", foreign_keys=[instructorId], back_populates="recordsi")
    wachiman = db.relationship("User", foreign_keys=[wachimanId], back_populates="recordsw")

    equipment = db.relationship("Equipments", back_populates="record")
