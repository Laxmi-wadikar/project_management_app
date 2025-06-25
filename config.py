import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-default-secret'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+mysqlconnector://flaskuser:tew%40123@localhost/flask_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
