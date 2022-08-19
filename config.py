# config.py
#  config file for backend
# by: mika senghaas

# imports
import os
import redis
from dotenv import load_dotenv

# load env
load_dotenv()

ENV = os.environ['ENV']
SECRET_KEY = os.environ['SECRET_KEY']
DATABASE_URI = os.environ['DATABASE_URI']
REDIS_URL = os.environ['REDISCLOUD_URL']

class Config:
  # dev env
  ENV = ENV

  # db
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SQLALCHEMY_ECHO = False
  SQLALCHEMY_DATABASE_URI = DATABASE_URI

  SECRET_KEY = SECRET_KEY
  SESSION_TYPE = "redis"
  SESSION_PERMANENT = False
  SESSION_USE_SIGNER = True
  SESSION_REDIS = redis.from_url(REDIS_URL)
