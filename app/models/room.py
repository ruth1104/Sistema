from app import db
import qrcode
import base64
from io import BytesIO
import json

class Rooms(db.Model):
   __tablename__ = 'room'
   idRoom = db.Column(db.Integer, primary_key=True)
   nameRoom = db.Column(db.String(255), nullable=False)
   
   roomLoan = db.relationship("RoomsLoans", back_populates="room", foreign_keys="RoomsLoans.roomId")
   
   def generate_qr(self):
        # Crea el contenido del QR como JSON
        qr_data = {
            "ID": self.idRoom,
            "nameRoom": self.nameRoom,
            
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