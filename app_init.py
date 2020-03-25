from flask import Flask
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

from environment import DB_URI, JWT_SECRET, BCRYPT_LOG_ROUNDS

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["BCRYPT_LOG_ROUNDS"] = BCRYPT_LOG_ROUNDS
app.config["JWT_SECRET"] = JWT_SECRET
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
