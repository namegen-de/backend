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
DB_URI = os.environ['DB_URI']
REDIS_URL = os.environ['REDISCLOUD_URL'] if 'REDISCLOUD_URL' in os.environ else os.environ['REDIS_LOCAL']

class Config:
  SECRET_KEY = os.environ["SECRET_KEY"]

  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SQLALCHEMY_ECHO = True
  SQLALCHEMY_DATABASE_URI = DB_URI

  SESSION_TYPE = 'redis'
  SESSION_PERMANENT = False
  SESSION_USE_SIGNER = True
  SESSION_REDIS = redis.from_url(REDIS_URL)
