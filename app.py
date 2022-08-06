# app.py
#  flask backend
# by: mika senghaas

# imports
import flask
from flask import Flask
from flask import (
  abort,
  session,
  request,
  jsonify
)
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_session import Session

# custom imports
from config import Config
from models import (
  db, 
  User,
  Name, 
  Like)

import sys
sys.path.append('../model')

from _utils import get_conversions, load_run
from sample import sample

# initialise flask app
app = Flask(__name__)
app.config.from_object(Config)

# addons
cors = CORS(app, supports_credentials=True) # enable cross origin
bcrypt = Bcrypt(app) # encrypt password
server_session = Session(app) # server side authentification
db.init_app(app) # sql alchemy postgres db handling

# load model
model, char2idx, country2idx, meta_data = load_run()
idx2char = {i: c for c, i in char2idx.items()}
a2i, i2a, a2c, c2a, c2i, i2c = get_conversions()

# init db
with app.app_context():
  db.create_all()

@app.route("/")
def home():
  return "Flask backend is running!"

# user routes
@app.route("/register", methods=["POST"])
def register_user():
  username = request.json["username"]
  email = request.json["email"]
  password = request.json["password"]

  user_exists = User.query.filter_by(email=email).first() is not None

  if user_exists:
    return jsonify({"error": "User already exists."}), 409

  # hash password and add new user
  hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
  new_user = User(username=username, email=email, password=hashed_password)
  
  # add user to session
  db.session.add(new_user)
  db.session.commit()

  return jsonify({
      "username": new_user.username,
      "id": new_user.id,
      "email": new_user.email,
  })

@app.route("/login", methods=["POST"])
def login_user():
  email = request.json["email"]
  password = request.json["password"]

  user = User.query.filter_by(email=email).first()

  if user is None:
    return jsonify({"error": "Email not registered."}), 401
  
  if not bcrypt.check_password_hash(user.password, password):
    return jsonify({"error": "Wrong password."}), 401

  session['user_id'] = user.id

  return jsonify({
      "username": user.username,
      "id": user.id,
      "email": user.email
  })

@app.route("/logout", methods=["POST"])
def logout_user():
  if 'user_id' not in session:
    return jsonify({"error": "No user logged in."}), 401
  session.pop('user_id')

  return 200

@app.route("/user_info", methods=["GET"])
def get_user_info():
  if 'user_id' not in session:
    return jsonify({"error": "Unauthorised"}), 409

  user_id = session['user_id']
  user = User.query.filter_by(id=user_id).first()
  
  return jsonify({
      "username": user.username,
      "id": user.id,
      "email": user.email
    })

@app.route("/likes", methods=["GET", "POST"])
def like_name():
  if 'user_id' not in session:
    return jsonify({"error": "Unauthorised"}), 409

  # user id from session
  uid = session['user_id']

  # get all user likes
  if flask.request.method == 'GET':
    likes = Like.query\
      .filter_by(uid=uid)\
      .order_by(Like.created_on)\
      .all()

    res = {l.nid: {"created_on": l.created_on} for l in likes}

    names = Name.query\
        .filter(Name.id.in_(res))\
        .all()

    for n in names:
      data = {"name": n.name, "countrycode": n.countrycode, "gender": n.gender}
      res[n.id].update(data)

    return jsonify(res)
    
  elif flask.request.method == 'POST':
    like = bool(request.json["like"])
    name = request.json["name"]
    countrycode = request.json["countrycode"]
    gender = request.json["gender"]
    
    name_exists = Name.query.filter_by(name=name, countrycode=countrycode, gender=gender).first() is not None
    if like:
      if not name_exists:
        new_name = Name(name=name, countrycode=countrycode, gender=gender)
        db.session.add(new_name)
        db.session.commit()
    
      nid = Name.query.filter_by(name=name, countrycode=countrycode, gender=gender).first().id
      already_liked = Like.query.filter_by(uid=uid, nid=nid).first() is not None

      if already_liked:
        return jsonify({"msg": "Name already liked."})
      like = Like(uid=uid, nid=nid)
      db.session.add(like)
      db.session.commit()

      return jsonify({
        "msg": "Sucessfully added to liked"
      })

    # unlike if exists
    else:
      if not name_exists:
        return jsonify({"msg": "Name does not exist"}), 401
      nid = Name.query.filter_by(name=name, countrycode=countrycode, gender=gender).first().id
      user_liked = Like.query.filter_by(uid=uid, nid=nid).first() is not None
      if not user_liked:
        return jsonify({"msg": "User has not liked name"}), 401

      Like.query.filter_by(uid=uid, nid=nid).delete()
      db.session.commit()

      return jsonify({"msg": "Successfully removed from likes"})

# model routes

# get model meta data
@app.route("/meta", methods=['GET'])
def meta():
  return jsonify(meta_data)

@app.route("/name", methods=["POST"])
def name():
  countrycode = request.json['countrycode']
  gender = request.json['gender']
  start_with = request.json['start_with']
  max_len = request.json['max_len']

  output = sample(
      model, 
      char2idx, 
      idx2char,
      a2i,
      i2a,
      countries=[countrycode],
      gender=gender,
      start_with=start_with,
      max_len=max_len)
    
  return jsonify(output)

if __name__ == '__main__':
  app.run(debug=True)