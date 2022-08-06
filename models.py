from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

db = SQLAlchemy()

def get_uuid():
  return uuid4().hex

class User(db.Model):
  __tablename__ = 'users'
  id = db.Column(db.String(32), primary_key=True, default=get_uuid())
  email = db.Column(db.String(350), nullable=False, unique=True)
  username = db.Column(db.String(32), nullable=False)
  password = db.Column(db.Text, nullable=False)
  created_on = db.Column(db.DateTime, server_default=db.func.now())

class Name(db.Model):
  __tablename__ = 'names'
  id = db.Column(db.String(32), primary_key=True, default=get_uuid())
  name = db.Column(db.String(32), nullable=False)
  countrycode = db.Column(db.CHAR(2), nullable=False)
  gender = db.Column(db.CHAR(1), nullable=False)
  created_on = db.Column(db.DateTime, server_default=db.func.now())

class Like(db.Model):
  __tablename__ = 'likes'
  uid = db.Column(db.String(32), db.ForeignKey('users.id'), primary_key=True)
  nid = db.Column(db.String(32), db.ForeignKey('names.id'), primary_key=True)
  created_on = db.Column(db.DateTime, server_default=db.func.now())