from flask import Flask
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

from environment import DATABASE_URL, JWT_SECRET, BCRYPT_LOG_ROUNDS

# Create all the global context for the flask app
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["BCRYPT_LOG_ROUNDS"] = BCRYPT_LOG_ROUNDS
app.config["JWT_SECRET"] = JWT_SECRET
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
