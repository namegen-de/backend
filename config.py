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

ENV = os.environ['ENV']
SECRET_KEY = os.environ['SECRET_KEY']
DATABASE_URL = os.environ['DATABASE_URL']
REDIS_URL = os.environ['REDISCLOUD_URL'] if 'REDISCLOUD_URL' in os.environ else os.environ['REDIS_LOCAL']

class Config:
  # dev env
  ENV = ENV

  # db
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SQLALCHEMY_ECHO = False
  SQLALCHEMY_DATABASE_URI = DATABASE_URL

  # session cookies
  SECRET_KEY = SECRET_KEY

  SESSION_TYPE = 'redis'
  SESSION_PERMANENT = False
  SESSION_USE_SIGNER = True
  SESSION_REDIS = redis.from_url(REDIS_URL)
