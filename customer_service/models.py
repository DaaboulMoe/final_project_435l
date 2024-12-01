from db import db

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    marital_status = db.Column(db.String(20), nullable=False)
    wallet_balance = db.Column(db.Float, default=0)
    is_admin = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "username": self.username,
            "age": self.age,
            "address": self.address,
            "gender": self.gender,
            "marital_status": self.marital_status,
            "wallet_balance": self.wallet_balance, 
        }
