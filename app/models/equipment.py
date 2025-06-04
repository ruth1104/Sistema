from app import db 
import qrcode
import base64
from io import BytesIO
import json

class Equipments(db.Model):
    __tablename__ = 'equipment'
    idEquipment = db.Column(db.Integer, primary_key=True)
    brandEquipment = db.Column(db.String(255), nullable=False)
    codeEquipment = db.Column(db.String(255), unique=True, nullable=True)
    accassoriesEquipment = db.Column(db.String(255), nullable=True)

    userId = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=True)
    apprenticeId = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=True)     # Aprendiz
    instructorId = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=True)     # Instructor

    # Relaciones con tabla User por rol
    user = db.relationship("User", back_populates="equipmentu", foreign_keys=[userId])
    apprentice = db.relationship("User", back_populates="equipmenta", foreign_keys=[apprenticeId])
    instructor = db.relationship("User", back_populates="equipmenti", foreign_keys=[instructorId])

    # Relaciones con tablas de registros
    record = db.relationship("Records", back_populates="equipment")
    recordsIn = db.relationship("RecordsIn", back_populates="equipment")

    def generate_qr(self):
        # Crea el contenido del QR como JSON
        qr_data = {
            "ID": self.idEquipment,
            "brandEquipment": self.brandEquipment,
            "codeEquipment": self.codeEquipment,
            "accassoriesEquipment": self.accassoriesEquipment,
        }

        # Serializa a JSON
        qr_data_json = json.dumps(qr_data)

        # Crea el QR
        qr = qrcode.QRCode(version=1, box_size=5, border=5)
        qr.add_data(qr_data_json)
        qr.make(fit=True)

        img = qr.make_image(fill="black", back_color="white")

        # Convierte a base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return img_base64
