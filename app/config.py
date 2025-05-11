import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    DEBUG = False
    TESTING = False
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/plant_disease')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt_secret_key')

class DevelopmentConfig(Config):
    DEBUG = True
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/plant_disease_dev')

class TestingConfig(Config):
    TESTING = True
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/plant_disease_test')

class ProductionConfig(Config):
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/plant_disease_prod')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
