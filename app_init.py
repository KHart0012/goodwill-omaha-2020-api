from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from environment import DB_URI, AZURE_ENVIRONMENT

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
