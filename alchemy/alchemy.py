import os

from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import current_app
from flask import Blueprint, render_template, url_for, redirect, session, request, flash, g

alchemy = Blueprint('alchemy', __name__, template_folder='templates', static_folder='static')

# current_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
# current_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_alchemy = SQLAlchemy()


@alchemy.route("/")
def index():
    # content = render_template('index.html', menu=dbase.getMenu(), posts=dbase.getPostsAnonce(), username=g.username)
    # print(111, make_response(content).__dict__)
    # print(db_alchemy)
    return '1111'


class Users(db_alchemy.Model):
    id = db_alchemy.Column(db_alchemy.Integer, primary_key=True)
    email = db_alchemy.Column(db_alchemy.String(50), unique=True)
    psw = db_alchemy.Column(db_alchemy.String(500), nullable=True)
    date = db_alchemy.Column(db_alchemy.DateTime, default=datetime.utcnow)

    pr = db_alchemy.relationship('Profiles', backref='users', uselist=False)

    def __repr__(self):
        return f"<users {self.id}>"


class Profiles(db_alchemy.Model):
    id = db_alchemy.Column(db_alchemy.Integer, primary_key=True)
    name = db_alchemy.Column(db_alchemy.String(50), nullable=True)
    old = db_alchemy.Column(db_alchemy.Integer)
    city = db_alchemy.Column(db_alchemy.String(100))

    user_id = db_alchemy.Column(db_alchemy.Integer, db_alchemy.ForeignKey('users.id'))

    def __repr__(self):
        return f"<profiles {self.id}>"
