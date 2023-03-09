import os
from os.path import join, dirname
from flask import Flask
from dotenv import load_dotenv
from rine.extensions import mongo, mail
from rine.main.routes import main

dotenv_path = join(dirname(__file__), '../.env')
print(dotenv_path)
load_dotenv(dotenv_path)

MONGO_URI = os.environ.get("MONGO_URI")
print(MONGO_URI)


def create_app():
    app = Flask(__name__)
    app.config['MONGO_URI'] = MONGO_URI
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = os.environ.get('SEND_TO')
    app.config['MAIL_PASSWORD'] = 'lvrhyizcmwtqmynj'
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    mongo.init_app(app)
    mail.init_app(app)
    app.register_blueprint(main)
    return app
