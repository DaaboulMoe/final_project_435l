import datetime
from db import db

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    comment = db.Column(db.String(500), nullable=True)
    moderated = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "product_id": self.product_id,
            "rating": self.rating,
            "comment": self.comment,
            "moderated": self.moderated,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }