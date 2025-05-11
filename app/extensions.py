from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt

# Initialize extensions
mongo = PyMongo()
bcrypt = Bcrypt()
cors = CORS()

def init_extensions(app: Flask):
    mongo.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)
