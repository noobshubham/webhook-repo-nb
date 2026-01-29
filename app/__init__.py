from flask import Flask
from flask_cors import CORS
import os

from dotenv import load_dotenv

# Loading variables from .env
load_dotenv()

from app.extensions import mongo
from app.webhook.routes import webhook


# Creating our flask app
def create_app():

    app = Flask(__name__)

    # Enable CORS
    CORS(app)

    # Setting Mongo Connection String
    app.config["MONGO_URI"] = os.getenv("MONGO_URL")
    
    mongo.init_app(app)

    # Ping Mongo to test Connection
    try:
        mongo.cx.admin.command("ping")
        print("MongoDB connected successfully")
    except Exception as e:
        print("MongoDB connection failed: ", e)
    
    # registering all the blueprints
    app.register_blueprint(webhook)
    
    return app
