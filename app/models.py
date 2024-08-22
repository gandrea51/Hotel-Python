from flask_login import UserMixin
from . import db

class User (UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique = True)
    password = db.Column(db.String(256))
    phone = db.Column(db.String(20))
    role = db.Column(db.String(50))

class Hotel (db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(256))
    room = db.Column(db.Integer)
    description = db.Column(db.Text)
    star = db.Column(db.Integer)

class Service (db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(5,2))
    duration = db.Column(db.String(100))
    available  = db.Column(db.String(2))

class Room (db.Model):
    id = db.Column(db.Integer, primary_key = True)
    type = db.Column(db.String(100))
    description = db.Column(db.Text)

class Booking (db.Model):
    id = db.Column(db.Integer, primary_key = True)
    state = db.Column(db.String(100))
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable = False)    
    hotel_id = db.Column(db.BigInteger, db.ForeignKey('hotel.id'), nullable = False)
    room_id = db.Column(db.BigInteger, db.ForeignKey('room.id'), nullable = False)

    user = db.relationship('User', backref = db.backref('bookings', lazy = True))
    hotel = db.relationship('Hotel', backref = db.backref('bookings', lazy = True))
    room = db.relationship('Room', backref = db.backref('bookings', lazy = True))
