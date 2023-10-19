from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from decouple import config
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config('SQLALCHEMY_DATABASE_URI')
#app.config['SQLALCHEMY_DATABASE_URI'] = config('SQLALCHEMY_DATABASE_URI_DEV')
db = SQLAlchemy(app)

from src import routes
