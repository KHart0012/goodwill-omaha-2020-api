from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

from environment import DB_URI, AZURE_ENVIRONMENT, JWT_SECRET

app = Flask(__name__)
app.config["BCRYPT_LOG_ROUNDS"] = 12
app.config["JWT_SECRET"] = JWT_SECRET
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
