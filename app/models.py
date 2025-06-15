from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import hashlib

db = SQLAlchemy()

roles = db.Table('equipment_responsibles',
    db.Column('equipment_id', db.Integer, db.ForeignKey('equipment.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    equipment = db.relationship('Equipment', backref='category', lazy=True)

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    inventory_number = db.Column(db.String(50), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum('active', 'repair', 'disposed', name='status_enum'), nullable=False)
    note = db.Column(db.Text)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    maintenance = db.relationship('Maintenance', backref='equipment', cascade="all, delete")
    disposal = db.relationship('Disposal', backref='equipment', uselist=False, cascade="all, delete")
    responsibles = db.relationship('User', secondary=roles, backref='assigned_equipment')

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(128), nullable=False)
    mime_type = db.Column(db.String(64), nullable=False)
    md5_hash = db.Column(db.String(64), nullable=False, unique=True)
    equipment = db.relationship('Equipment', backref='image', uselist=False)

class Maintenance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.Text)

class Disposal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    disposal_date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    pdf_filename = db.Column(db.String(128), nullable=False)


def generate_md5(file_data):
    return hashlib.md5(file_data).hexdigest()