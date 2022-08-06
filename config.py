# config.py
#  config file for backend
# by: mika senghaas

# imports
import os
import json
import redis
from dotenv import load_dotenv

# load env
load_dotenv()

class Config:
  SECRET_KEY = os.environ["SECRET_KEY"]

  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SQLALCHEMY_ECHO = True
  SQLALCHEMY_DATABASE_URI = os.environ["DB_URI"]

  SESSION_TYPE = 'redis'
  SESSION_PERMANENT = False
  SESSION_USE_SIGNER = True
  SESSION_REDIS = redis.from_url("redis://127.0.0.1:6379")