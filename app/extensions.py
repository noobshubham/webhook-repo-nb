from flask_pymongo import PyMongo

# Setup MongoDB here
mongo = PyMongo()

def init_db(app):
    mongo.init_app(app)
