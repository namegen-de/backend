# app.py
#  flask backend
# by: mika senghaas

# imports
import flask
from flask import Flask
from flask import session, request, jsonify

# flask addons
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

# load rnn model
from model import (
    load_model, 
    sample)

# initialise flask app
app = Flask(__name__)
app.config.from_object(Config)

# allow cross-origin
cors = CORS(app, supports_credentials=True) # enable cross origin

# password encryption
bcrypt = Bcrypt(app) # encrypt password

# cookies for secure server-side auth and user sessions
user_session = Session(app)

# sql alchemy postgres db handling
db.init_app(app) 

# load model
model, meta_data = load_model()

# init db
with app.app_context():
  db.create_all()

@app.route("/api")
def home():
  return f"Flask backend is running! [ENV={Config.ENV}]"


# user routes
@app.route("/api/register", methods=["POST"])
def register():
  username = request.json["username"]
  email = request.json["email"]
  password = request.json["password"]

  user_exists = User.query.filter_by(email=email).first() is not None

  if user_exists:
    return jsonify({"error": "User already exists."}), 409

  # hash password and add new user
  hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
  new_user = User(username, email, hashed_password)
  
  # add user to session
  db.session.add(new_user)
  db.session.commit()

  return jsonify({
      "msg": "User successfully registered"
  }), 200

@app.route("/api/login", methods=["POST"])
def login_user():
  email = request.json["email"]
  password = request.json["password"]

  user = User.query.filter_by(email=email).first()

  if user is None:
    return jsonify({"error": "Email not registered."}), 401
  
  if not bcrypt.check_password_hash(user.password, password):
    return jsonify({"error": "Wrong password."}), 401

  # save session cookie
  session['user_id'] = user.id

  return jsonify({
      "msg": "Sucessfully logged in",
      "user": {"username": user.username, "email": user.email}
      }), 200

@app.route("/api/logout", methods=["POST"])
def logout_user():
  if not 'user_id' in session:
    return jsonify({"msg": "No user logged in"}), 401
  session.pop('user_id')
  return jsonify({"msg": "Successfully logged out"}), 200

@app.route("/api/@me", methods=["GET"])
def get_user_info():
  user_id = session.get('user_id')

  if not user_id:
    return jsonify({
        "msg": "Unauthorised"
        }), 401

  user = User.query.filter_by(id=user_id).first()
  
  return jsonify({
      "id": user.id,
      "username": user.username,
      "email": user.email
    }), 200

@app.route("/api/likes", methods=["GET", "POST"])
def like_name():
  if 'user_id' not in session:
    return jsonify({"error": "Unauthorised"}), 401

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

    return jsonify(res), 200
    
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
      }), 200

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

      return jsonify({
          "msg": "Successfully removed from likes"
          }), 200

# model routes

# get model meta data
@app.route("/api/meta", methods=['GET'])
def meta():
  return jsonify(meta_data)

@app.route("/api/name", methods=["POST"])
def name():
  countrycode = request.json['countrycode']
  gender = request.json['gender']
  start_with = request.json['start_with']
  max_len = request.json['max_len']

  output = sample(
      model, 
      countries=[countrycode],
      gender=gender,
      start_with=start_with,
      max_len=max_len)
    
  return jsonify(output)

if __name__ == '__main__':
  if Config.ENV == 'DEV':
    app.run(debug=True)
  else:
    app.run()
