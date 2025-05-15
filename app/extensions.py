from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from gridfs import GridFS
from pymongo import MongoClient

# Initialize extensions
mongo = PyMongo()
bcrypt = Bcrypt()
cors = CORS()
fs = None  # GridFS instance (initialized in init_extensions)

def init_extensions(app: Flask):
    mongo.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)
    
    # Initialize GridFS after PyMongo is initialized
    global fs
    fs = GridFS(mongo.db)
